import asyncio
import secrets
import time
from contextlib import suppress
from dataclasses import dataclass, field

import chess

from .game import GameError, board_state, color_name
from .hints import HintPlan

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


@dataclass
class Room:
    code: str
    mode: str
    board: chess.Board = field(default_factory=chess.Board)
    players: dict = field(default_factory=lambda: {chess.WHITE: secrets.token_urlsafe(32)})
    connections: dict = field(default_factory=dict)
    hint_levels: dict = field(default_factory=dict)
    hint_cache: HintPlan | None = None
    revealed: set = field(default_factory=set)
    last_san: str | None = None
    created_at: float = field(default_factory=time.monotonic)
    last_activity: float = field(default_factory=time.monotonic)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def identify(self, token: str) -> chess.Color:
        for color, expected in self.players.items():
            if secrets.compare_digest(token, expected):
                return color
        raise GameError("INVALID_TOKEN", "Não foi possível recuperar seu lugar nesta sala.")

    def credentials(self, color: chess.Color) -> dict:
        return {"code": self.code, "color": color_name(color), "player_token": self.players[color], "mode": self.mode}

    def hint_payload(self, color: chess.Color) -> dict:
        level = self.hint_levels[color]
        messages = self.hint_cache.messages
        response = {"type": "hint", "level": level, "message": messages[level - 1],
                    "messages": list(messages[:level]), "ply": len(self.board.move_stack)}
        return response

    def reveal_payload(self) -> dict:
        plan = self.hint_cache
        return {"type": "reveal", "move": plan.move, "san": plan.san,
                "explanation": plan.explanation, "source": plan.source,
                "ply": len(self.board.move_stack)}

    def state(self) -> dict:
        state = board_state(self.board)
        if chess.BLACK not in self.players:
            state["status"] = "waiting"
            state["legal_moves"] = []
        return {"type": "state", "code": self.code, "mode": self.mode, **state,
                "last_san": self.last_san,
                "players": {color_name(c): {"joined": c in self.players, "connected": c in self.connections} for c in (chess.WHITE, chess.BLACK)}}

    async def broadcast(self) -> None:
        # Chamado sob lock: todos recebem as posições na mesma ordem.
        # Remove conexões quebradas e transmite a presença corrigida.
        for _ in range(2):
            state = self.state()
            connections = list(self.connections.items())

            async def send(ws):
                await asyncio.wait_for(ws.send_json(state), timeout=3)

            results = await asyncio.gather(*(send(ws) for _, ws in connections), return_exceptions=True)
            removed = False
            for (color, ws), result in zip(connections, results):
                if isinstance(result, BaseException) and self.connections.get(color) is ws:
                    del self.connections[color]
                    removed = True
                    with suppress(Exception):
                        await asyncio.wait_for(ws.close(code=1011), timeout=1)
            if not removed:
                break


class RoomManager:
    def __init__(self, ttl_seconds: int = 86400, max_rooms: int = 500):
        self.rooms: dict[str, Room] = {}
        self.ttl_seconds = ttl_seconds
        self.max_rooms = max_rooms

    def cleanup(self):
        now = time.monotonic()
        expired = [code for code, room in self.rooms.items() if not room.connections and now - room.last_activity > self.ttl_seconds]
        for code in expired:
            del self.rooms[code]

    def create(self, mode: str) -> Room:
        self.cleanup()
        if len(self.rooms) >= self.max_rooms:
            raise GameError("SERVER_FULL", "O servidor está cheio. Tente novamente mais tarde.")
        while True:
            code = "".join(secrets.choice(ALPHABET) for _ in range(6))
            if code not in self.rooms:
                break
        room = Room(code=code, mode=mode)
        self.rooms[code] = room
        return room

    def get(self, code: str) -> Room:
        self.cleanup()
        room = self.rooms.get(code.upper())
        if room is None:
            raise GameError("ROOM_NOT_FOUND", "Sala não encontrada. Confira o código; ela pode ter expirado.")
        return room

    def join(self, code: str) -> Room:
        room = self.get(code)
        if chess.BLACK in room.players:
            raise GameError("ROOM_FULL", "Essa sala já tem dois jogadores.")
        room.players[chess.BLACK] = secrets.token_urlsafe(32)
        room.last_activity = time.monotonic()
        return room
