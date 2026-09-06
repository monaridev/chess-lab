"""In-memory Solo sessions; intentions and version checks, never client boards."""
import asyncio
from dataclasses import dataclass, field
import secrets
import time
from typing import Literal

import chess
from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, ConfigDict, Field

from .game import GameError, board_state, outcome, play
from .hints import build_plan
from .learning import Uci
from .move_review import public_review, review_move, summary
from .schemas import MoveIntent
from .solo_engine import SoloEngine


class StartSolo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    difficulty: Literal["beginner", "easy", "medium", "hard"] = "beginner"
    color: Literal["white", "black"] = "white"
    help_mode: Literal["review", "progressive"] = "progressive"


class SoloIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["move", "reply", "hint", "reveal", "resign"]
    ply: int = Field(ge=0)
    move: Uci | None = None
    confirmed: bool = False


@dataclass
class Session:
    color: chess.Color
    difficulty: str
    help_mode: str
    board: chess.Board = field(default_factory=chess.Board)
    reviews: list = field(default_factory=list)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    last_activity: float = field(default_factory=time.monotonic)
    resigned: bool = False
    hint_level: int = 0
    hint_plan: object = None
    revealed: bool = False

    def state(self):
        state = board_state(self.board)
        if self.resigned:
            state.update(status="finished", termination="resignation", result="0-1" if self.color else "1-0",
                         winner="black" if self.color else "white", legal_moves=[])
        return {"board": state, "color": "white" if self.color else "black", "difficulty": self.difficulty,
                "help_mode": self.help_mode, "review": public_review(self.reviews[-1]) if self.reviews else None,
                "history": [public_review(r) for r in self.reviews], "summary": summary(self.reviews),
                "hint_level": self.hint_level, "hints": list(self.hint_plan.messages[:self.hint_level]) if self.hint_plan else [],
                "reveal": {"move": self.hint_plan.move, "message": self.hint_plan.explanation} if self.revealed else None}


class SoloManager:
    def __init__(self, engine=None, capacity=100, ttl=86400):
        self.engine = engine if engine is not None else SoloEngine()
        self.sessions = {}
        self.capacity, self.ttl = capacity, ttl

    def cleanup(self):
        now = time.monotonic()
        for token, session in list(self.sessions.items()):
            if not session.lock.locked() and now - session.last_activity > self.ttl:
                del self.sessions[token]

    def get(self, token):
        self.cleanup()
        session = self.sessions.get(token)
        if session is None:
            raise GameError("SOLO_NOT_FOUND", "Partida Solo não encontrada ou expirada. Comece uma nova partida.")
        session.last_activity = time.monotonic()
        return session

    async def start(self, options):
        self.cleanup()
        if len(self.sessions) >= self.capacity:
            raise GameError("SERVER_FULL", "Há muitas partidas abertas. Tente novamente mais tarde.")
        # Require real scored analysis before advertising a working Solo game.
        await self.engine.candidates(chess.Board(), options.color == "white")
        # Capacity recheck after yielding to the engine.
        if len(self.sessions) >= self.capacity:
            raise GameError("SERVER_FULL", "Há muitas partidas abertas. Tente novamente mais tarde.")
        token = secrets.token_urlsafe(32)
        session = Session(options.color == "white", options.difficulty, options.help_mode)
        self.sessions[token] = session
        return {"token": token, **session.state()}

    async def act(self, session, intent):
        async with session.lock:
            board = session.board
            if intent.ply != len(board.move_stack):
                raise GameError("STALE_POSITION", "A posição mudou. Atualize a partida antes de continuar.")
            if session.resigned or outcome(board):
                raise GameError("GAME_OVER", "A partida já terminou.")
            if intent.action == "resign":
                if not intent.confirmed:
                    raise GameError("CONFIRM_REQUIRED", "Confirme para encerrar a partida.")
                session.resigned = True
            elif intent.action == "reply":
                if board.turn == session.color:
                    raise GameError("NOT_ENGINE_TURN", "Agora é sua vez.")
                move = await self.engine.choose(board, session.difficulty)
                if move not in board.legal_moves:
                    raise GameError("ENGINE_UNAVAILABLE", "Stockfish não retornou uma jogada legal. Tente novamente.")
                board.push(move)
                session.hint_level, session.hint_plan, session.revealed = 0, None, False
            elif intent.action == "move":
                if intent.move is None:
                    raise GameError("INVALID_MOVE", "Escolha uma peça e seu destino.")
                after = board.copy(stack=True)
                uci = intent.move
                play(after, session.color, MoveIntent.model_validate({"type": "move", "from": uci[:2], "to": uci[2:4], "promotion": uci[4:] or None}))
                candidates = await self.engine.candidates(board, session.color)
                played = (await self.engine.candidates(after, session.color))[0]
                review = await asyncio.to_thread(review_move, board.copy(stack=True), chess.Move.from_uci(uci), after, candidates, played)
                # Commit only after both evaluations succeed. A failed request loses no move.
                session.board = after
                session.reviews.append(review)
                session.hint_level, session.hint_plan, session.revealed = 0, None, False
            else:
                if board.turn != session.color:
                    raise GameError("NOT_YOUR_TURN", "Peça uma dica quando for sua vez.")
                if session.help_mode != "progressive":
                    raise GameError("HINTS_DISABLED", "Esta partida usa apenas revisão após o lance.")
                if intent.action == "reveal" and (not intent.confirmed or session.hint_level < 4):
                    raise GameError("HINTS_FIRST", "Explore as quatro pistas e confirme antes de revelar.")
                if session.hint_plan is None:
                    candidates = await self.engine.candidates(board, session.color)
                    session.hint_plan = await asyncio.to_thread(build_plan, board.copy(stack=True), candidates[0].move, "stockfish")
                if intent.action == "hint":
                    session.hint_level = min(4, session.hint_level + 1)
                else:
                    session.revealed = True
            session.last_activity = time.monotonic()
            return session.state()


router = APIRouter(prefix="/api/solo")


@router.post("", status_code=201)
async def start(body: StartSolo, request: Request):
    return await request.app.state.solo.start(body)


@router.get("")
async def state(request: Request, x_solo_token: str = Header(default="")):
    session = request.app.state.solo.get(x_solo_token)
    async with session.lock:
        return session.state()


@router.post("/action")
async def action(body: SoloIntent, request: Request, x_solo_token: str = Header(default="")):
    manager = request.app.state.solo
    return await manager.act(manager.get(x_solo_token), body)
