import asyncio
import time

import chess
import chess.engine
import pytest
from fastapi.testclient import TestClient

from backend.analysis import AnalysisService, LOCAL_ENGINE
from backend.hints import build_plan
from backend.main import create_app
from backend.rooms import RoomManager
from tests.conftest import connected_pair, move_both, move_payload, new_pair


def test_missing_engine_fallback_cache_and_board_unchanged():
    async def run():
        service = AnalysisService(path="/no/such/stockfish")
        board = chess.Board()
        before = board.fen()
        plan = await service.plan(board)
        assert plan.source == "heuristic" and service.failed
        assert chess.Move.from_uci(plan.move) in board.legal_moves
        assert board.fen() == before and not board.move_stack
        assert await service.plan(board) is plan
        await service.close()
    asyncio.run(run())


@pytest.mark.parametrize("failure", ["timeout", "crash", "illegal"])
def test_engine_failure_does_not_break_hints_or_block_loop(monkeypatch, failure):
    async def run():
        closed = []
        class Transport:
            def close(self):
                closed.append(True)
        class Engine:
            async def configure(self, options):
                assert options == {"Threads": 1, "Hash": 32}
            async def analyse(self, board, limit, **kwargs):
                if failure == "timeout":
                    await asyncio.sleep(10)
                if failure == "crash":
                    raise chess.engine.EngineTerminatedError("engine terminou")
                return [{"pv": [chess.Move.from_uci("a1a8")]}]
        async def launch(path):
            return Transport(), Engine()
        monkeypatch.setattr(chess.engine, "popen_uci", launch)
        service = AnalysisService(path="fake", timeout=0.04)
        task = asyncio.create_task(service.plan(chess.Board()))
        tick = time.monotonic()
        await asyncio.sleep(0.01)
        assert time.monotonic() - tick < 0.2
        plan = await asyncio.wait_for(task, 2)
        assert plan.source == "heuristic"
        await service.close()
        assert closed
    asyncio.run(run())


def test_cache_is_bounded_and_distinguishes_positions():
    async def run():
        service = AnalysisService(path="", cache_size=2)
        board = chess.Board()
        initial = board.fen()
        for uci in ("e2e4", "e7e5", "g1f3"):
            await service.plan(board)
            board.push_uci(uci)
        assert len(service.cache) == 2 and initial not in service.cache
    asyncio.run(run())


def test_busy_engine_uses_fallback_without_waiting_forever():
    async def run():
        service = AnalysisService(path="fake")
        await service.lock.acquire()
        try:
            plan = await asyncio.wait_for(service.plan(chess.Board()), 1.5)
            assert plan.source == "heuristic" and not service.failed
        finally:
            service.lock.release()
    asyncio.run(run())


@pytest.mark.parametrize("fen,uci,concept", [
    ("1r6/4k3/8/4N3/8/8/8/4K3 w - - 0 1", "e5c6", "garfo"),
    ("4k3/8/2n5/8/8/8/8/4KB2 w - - 0 1", "f1b5", "cravada"),
    ("8/P6k/8/8/8/8/7p/4K3 w - - 0 1", "a7a8q", "promoção"),
    ("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2", "e5d6", "en passant"),
    ("4k3/8/8/8/8/8/4r3/4K3 w - - 0 1", "e1e2", "sair do xeque"),
    (chess.STARTING_FEN, "g1f3", "desenvolvimento"),
    ("7k/8/5KQ1/8/8/8/8/8 w - - 0 1", "g6g7", "rede de mate"),
])
def test_position_specific_pedagogy_never_contains_exact_move(fen, uci, concept):
    board = chess.Board(fen)
    plan = build_plan(board, chess.Move.from_uci(uci), "stockfish")
    assert plan.concept == concept
    assert len(plan.messages) == 4 and len(set(plan.messages)) == 4
    text = " ".join(plan.messages)
    assert uci not in text and "→" not in text
    assert uci[2:4] not in text
    assert plan.move == uci and plan.san == board.san(chess.Move.from_uci(uci))
    assert board.fen() == chess.Board(fen).fen()


def test_reveal_is_separate_private_confirmed_and_resets(client, manager):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        for level in range(1, 5):
            w.send_json({"type": "hint"})
            hint = w.receive_json()
            assert hint["level"] == level
            assert all(k not in hint for k in ("move", "san", "pv", "explanation"))
        for invalid in ({"type": "reveal", "ply": 0}, {"type": "reveal", "confirmed": False, "ply": 0}):
            w.send_json(invalid)
            assert w.receive_json()["code"] == "INVALID_MESSAGE"
        w.send_json({"type": "reveal", "confirmed": True, "ply": 3})
        assert w.receive_json()["code"] == "STALE_ANALYSIS"
        b.send_json({"type": "reveal", "confirmed": True, "ply": 0})
        assert b.receive_json()["code"] == "NOT_YOUR_TURN"
        w.send_json({"type": "reveal", "confirmed": True, "ply": 0})
        reveal = w.receive_json()
        assert reveal["type"] == "reveal" and reveal["explanation"]
        assert chess.Move.from_uci(reveal["move"]) in manager.get(white["code"]).board.legal_moves
        # O outro jogador recebe o próximo state, sem a dica/revelação privada.
        move_both(w, b, "e2e4")
        assert not manager.get(white["code"]).revealed


def test_reveal_without_hints_and_reconnect_restores_it(client):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        w.send_json({"type": "reveal", "confirmed": True, "ply": 0})
        reveal = w.receive_json()
        assert reveal["type"] == "reveal"
    with client.websocket_connect(f"/ws/{white['code']}") as w:
        w.send_json({"type": "auth", "token": white["player_token"]})
        assert w.receive_json()["type"] == "state"
        assert w.receive_json() == reveal


def test_normal_mode_rejects_reveal(client):
    white, black = new_pair(client, "normal")
    with connected_pair(client, white, black) as (w, b):
        w.send_json({"type": "reveal", "confirmed": True, "ply": 0})
        assert w.receive_json()["code"] == "HINTS_DISABLED"


@pytest.mark.parametrize("request_type", ["hint", "reveal"])
def test_analysis_does_not_lock_room_and_obsolete_answer_is_discarded(request_type):
    class SlowAnalysis:
        async def plan(self, board):
            await asyncio.sleep(0.3)
            return build_plan(board)
        async def close(self):
            pass
    manager = RoomManager()
    with TestClient(create_app(manager, SlowAnalysis())) as client:
        white, black = new_pair(client)
        with connected_pair(client, white, black) as (w, b):
            w.send_json({"type": "hint"} if request_type == "hint" else {"type": "reveal", "confirmed": True, "ply": 0})
            w.send_json(move_payload("e2e4"))
            state = w.receive_json()
            assert state["type"] == "state" and state["last_move"] == "e2e4"
            assert b.receive_json() == state
            stale = w.receive_json()
            assert stale["code"] == "STALE_ANALYSIS" and stale["ply"] == 0
            assert manager.get(white["code"]).hint_cache is None
            assert not manager.get(white["code"]).revealed


def test_real_stockfish_analyzes_and_never_mutates_board():
    if not LOCAL_ENGINE.is_file():
        pytest.skip("Stockfish local opcional não instalado")
    async def run():
        service = AnalysisService(path=str(LOCAL_ENGINE))
        board = chess.Board("7k/8/5KQ1/8/8/8/8/8 w - - 0 1")
        original = board.fen()
        plan = await service.plan(board)
        try:
            assert plan.source == "stockfish"
            move = chess.Move.from_uci(plan.move)
            assert move in board.legal_moves
            after = board.copy()
            after.push(move)
            assert after.is_checkmate()
            assert board.fen() == original
            assert plan.concept == "rede de mate"
        finally:
            await service.close()
    asyncio.run(run())
