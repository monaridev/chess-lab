import asyncio
import time
from contextlib import asynccontextmanager, suppress
from pathlib import Path

import chess
import anyio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .learning import router as learning_router
from .game import GameError, outcome, play
from .analysis import AnalysisService
from .rooms import RoomManager
from .schemas import Authenticate, CreateRoom, HintIntent, RevealIntent, intent_adapter

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"


async def receive_text(ws: WebSocket) -> str:
    message = await ws.receive()
    if message["type"] == "websocket.disconnect":
        raise WebSocketDisconnect(message.get("code", 1000))
    if "text" not in message:
        raise GameError("INVALID_MESSAGE", "Envie mensagens JSON em texto.")
    return message["text"]


def create_app(manager: RoomManager | None = None, analysis: AnalysisService | None = None) -> FastAPI:
    rooms = manager if manager is not None else RoomManager()
    analyser = analysis if analysis is not None else AnalysisService()

    @asynccontextmanager
    async def lifespan(app):
        async def cleanup():
            while True:
                await asyncio.sleep(60)
                rooms.cleanup()

        task = asyncio.create_task(cleanup())
        yield
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
        await analyser.close()

    app = FastAPI(title="Chess Lab", lifespan=lifespan)
    app.include_router(learning_router)
    app.state.rooms = rooms
    app.state.analysis = analyser

    @app.exception_handler(GameError)
    async def game_error(request: Request, exc: GameError):
        status = {"ROOM_NOT_FOUND": 404, "ROOM_FULL": 409, "SERVER_FULL": 503}.get(exc.code, 400)
        return JSONResponse(exc.payload(), status_code=status)

    @app.middleware("http")
    async def response_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'"
        return response

    @app.get("/")
    async def index():
        return FileResponse(FRONTEND / "index.html")

    @app.get("/api/health")
    async def health():
        return {"status": "ok"}

    @app.post("/api/rooms", status_code=201)
    async def create_room(body: CreateRoom):
        return rooms.create(body.mode).credentials(chess.WHITE)

    @app.post("/api/rooms/{code}/join")
    async def join_room(code: str):
        room = rooms.join(code)
        async with room.lock:
            await room.broadcast()
        return room.credentials(chess.BLACK)

    @app.websocket("/ws/{code}")
    async def websocket_endpoint(ws: WebSocket, code: str):
        await ws.accept()
        room = None
        color = None
        hint_task = None

        async def deliver_help(intent, snapshot, ply):
            try:
                plan = room.hint_cache or await analyser.plan(snapshot)
                async with room.lock:
                    if room.connections.get(color) is not ws:
                        return
                    if len(room.board.move_stack) != ply or room.board.fen() != snapshot.fen():
                        await ws.send_json({**GameError("STALE_ANALYSIS", "A posição mudou. Peça uma nova dica.").payload(), "ply": ply})
                        return
                    room.hint_cache = plan
                    if isinstance(intent, RevealIntent):
                        room.revealed.add(color)
                        await ws.send_json(room.reveal_payload())
                    else:
                        room.hint_levels[color] = min(room.hint_levels.get(color, 0) + 1, 4)
                        await ws.send_json(room.hint_payload(color))
            except (WebSocketDisconnect, RuntimeError, OSError):
                pass

        try:
            room = rooms.get(code)
            raw = await asyncio.wait_for(receive_text(ws), timeout=10)
            if len(raw) > 1024:
                raise GameError("INVALID_TOKEN", "Credencial inválida.")
            try:
                auth = Authenticate.model_validate_json(raw)
            except ValidationError:
                raise GameError("INVALID_TOKEN", "Reconecte usando a sessão original da sala.")
            color = room.identify(auth.token)
            async with room.lock:
                previous = room.connections.get(color)
                room.connections[color] = ws
                room.last_activity = time.monotonic()
                if previous:
                    with suppress(Exception):
                        await asyncio.wait_for(previous.close(code=4001, reason="Sessão aberta em outra conexão"), timeout=2)
                await room.broadcast()
                if room.hint_levels.get(color):
                    await ws.send_json(room.hint_payload(color))
                if color in room.revealed:
                    await ws.send_json(room.reveal_payload())
            while True:
                try:
                    raw = await receive_text(ws)
                    if len(raw) > 4096:
                        raise GameError("INVALID_MESSAGE", "Mensagem muito grande.")
                    intent = intent_adapter.validate_json(raw)
                    async with room.lock:
                        if room.connections.get(color) is not ws:
                            break
                        room.last_activity = time.monotonic()
                        if chess.BLACK not in room.players:
                            raise GameError("WAITING_FOR_OPPONENT", "Aguarde o segundo jogador entrar.")
                        if isinstance(intent, (HintIntent, RevealIntent)):
                            if room.mode != "assisted":
                                raise GameError("HINTS_DISABLED", "Dicas estão disponíveis na Partida Assistida.")
                            if outcome(room.board):
                                raise GameError("GAME_OVER", "A partida já terminou.")
                            if room.board.turn != color:
                                raise GameError("NOT_YOUR_TURN", "Peça uma dica quando for sua vez.")
                            if isinstance(intent, RevealIntent) and intent.ply != len(room.board.move_stack):
                                raise GameError("STALE_ANALYSIS", "A posição mudou. Confirme a revelação para a posição atual.")
                            if hint_task is not None and not hint_task.done():
                                raise GameError("ANALYSIS_PENDING", "Uma dica já está sendo preparada para você.")
                            hint_task = asyncio.create_task(deliver_help(intent, room.board.copy(stack=True), len(room.board.move_stack)))
                        else:
                            room.last_san = play(room.board, color, intent)
                            room.hint_levels.clear()
                            room.hint_cache = None
                            room.revealed.clear()
                            await room.broadcast()
                except ValidationError:
                    await ws.send_json(GameError("INVALID_MESSAGE", "Mensagem inválida. Envie uma jogada ou um pedido de dica.").payload())
                except GameError as exc:
                    await ws.send_json(exc.payload())
        except GameError as exc:
            with suppress(Exception):
                await ws.send_json(exc.payload())
                await ws.close(code=4003)
        except asyncio.TimeoutError:
            with suppress(Exception):
                await ws.close(code=4003, reason="Tempo de identificação esgotado")
        except (WebSocketDisconnect, RuntimeError, OSError):
            pass
        finally:
            # O cancelamento ASGI também precisa concluir a atualização de presença.
            with anyio.CancelScope(shield=True):
                if hint_task is not None:
                    hint_task.cancel()
                    with suppress(asyncio.CancelledError):
                        await hint_task
                if room is not None and color is not None:
                    async with room.lock:
                        if room.connections.get(color) is ws:
                            del room.connections[color]
                            room.last_activity = time.monotonic()
                            await room.broadcast()

    app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
    return app


app = create_app()
