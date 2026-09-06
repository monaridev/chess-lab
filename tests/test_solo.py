import asyncio
import random

import chess
import chess.engine
import pytest
from fastapi.testclient import TestClient

from backend.analysis import AnalysisService, LOCAL_ENGINE
from backend.game import GameError, outcome
from backend.main import create_app
from backend.solo import Session, SoloIntent, SoloManager, StartSolo
from backend.solo_engine import Candidate, DIFFICULTIES, SoloEngine


class FakeEngine:
    """Deterministic legal engine double; real Stockfish is tested separately."""
    def __init__(self):
        self.fail = False
    async def candidates(self, board, color):
        if self.fail:
            raise GameError("ENGINE_UNAVAILABLE", "Engine desligada")
        return [Candidate(next(iter(board.legal_moves), None), 0)]
    async def choose(self, board, difficulty):
        if self.fail:
            raise GameError("ENGINE_UNAVAILABLE", "Engine desligada")
        return next(iter(board.legal_moves))
    async def close(self):
        pass


@pytest.fixture
def solo_client():
    manager = SoloManager(FakeEngine())
    with TestClient(create_app(analysis=AnalysisService(path=""), solo=manager)) as client:
        yield client, manager


def begin(client, **options):
    response = client.post('/api/solo', json=options)
    assert response.status_code == 201, response.text
    data = response.json()
    return data, {'X-Solo-Token': data['token']}


def act(client, headers, action, ply, **fields):
    return client.post('/api/solo/action', headers=headers, json={'action': action, 'ply': ply, **fields})


def test_session_moves_version_reconnect_and_finish(solo_client):
    client, manager = solo_client
    data, headers = begin(client)
    token = data['token']
    assert data['board']['ply'] == 0 and data['summary']['accuracy'] is None
    assert client.get('/api/solo').json()['code'] == 'SOLO_NOT_FOUND'
    for uci, code in [('e7e5', 'OPPONENT_PIECE'), ('e2e5', 'ILLEGAL_MOVE')]:
        assert act(client, headers, 'move', 0, move=uci).json()['code'] == code
        assert manager.get(token).board.fen() == chess.STARTING_FEN
    data = act(client, headers, 'move', 0, move='g1f3').json()
    assert data['board']['ply'] == 1 and data['review']['comment']
    assert len(data['history']) == 1 and data['review']['label'] == 'Excelente'
    assert not {'best_move', 'before_cp', 'after_cp', 'loss'} & data['review'].keys()
    assert act(client, headers, 'move', 0, move='e2e4').json()['code'] == 'STALE_POSITION'
    assert act(client, headers, 'move', 1, move='e2e4').json()['code'] == 'NOT_YOUR_TURN'
    assert client.get('/api/solo', headers=headers).json() == data
    data = act(client, headers, 'reply', 1).json()
    assert data['board']['ply'] == 2 and len(data['history']) == 1
    assert act(client, headers, 'reply', 1).json()['code'] == 'STALE_POSITION'
    assert act(client, headers, 'resign', 2).json()['code'] == 'CONFIRM_REQUIRED'
    data = act(client, headers, 'resign', 2, confirmed=True).json()
    assert data['board']['status'] == 'finished' and data['board']['winner'] == 'black'
    assert data['summary']['reviewed_moves'] == 1
    assert act(client, headers, 'move', 2, move='e2e4').json()['code'] == 'GAME_OVER'


def test_help_progressive_separate_confirmed_and_reset(solo_client):
    client, _ = solo_client
    _, headers = begin(client)
    assert act(client, headers, 'reveal', 0, confirmed=True).json()['code'] == 'HINTS_FIRST'
    for level in range(1, 5):
        data = act(client, headers, 'hint', 0).json()
        assert len(data['hints']) == level and data['reveal'] is None
    assert act(client, headers, 'reveal', 0).json()['code'] == 'HINTS_FIRST'
    data = act(client, headers, 'reveal', 0, confirmed=True).json()
    assert data['reveal']['move'] and data['board']['ply'] == 0
    assert client.get('/api/solo', headers=headers).json()['reveal'] == data['reveal']
    assert act(client, headers, 'move', 0, move='e2e4').json()['hint_level'] == 0
    _, headers = begin(client, help_mode='review')
    assert act(client, headers, 'hint', 0).json()['code'] == 'HINTS_DISABLED'
    _, headers = begin(client, color='black')
    assert act(client, headers, 'hint', 0).json()['code'] == 'NOT_YOUR_TURN'
    assert act(client, headers, 'reply', 0).json()['board']['turn'] == 'black'


def test_input_boundaries_and_session_isolation(solo_client):
    client, _ = solo_client
    for options in ({'fen': chess.STARTING_FEN}, {'difficulty': 'impossible'}, {'help_mode': 'llm'}):
        assert client.post('/api/solo', json=options).status_code == 422
    _, a = begin(client)
    _, b = begin(client)
    assert act(client, a, 'move', 0, move='e2e4', fen=chess.STARTING_FEN).status_code == 422
    act(client, a, 'move', 0, move='e2e4')
    assert client.get('/api/solo', headers=b).json()['board']['ply'] == 0


def test_engine_failure_is_atomic_and_existing_modes_survive(solo_client):
    client, manager = solo_client
    data, headers = begin(client)
    manager.engine.fail = True
    assert act(client, headers, 'move', 0, move='e2e4').json()['code'] == 'ENGINE_UNAVAILABLE'
    assert manager.get(data['token']).board.fen() == chess.STARTING_FEN
    assert not manager.get(data['token']).reviews
    assert client.post('/api/rooms', json={'mode': 'normal'}).status_code == 201
    manager.engine.fail = False
    act(client, headers, 'move', 0, move='e2e4')
    manager.engine.fail = True
    assert act(client, headers, 'reply', 1).json()['code'] == 'ENGINE_UNAVAILABLE'
    assert client.get('/api/solo', headers=headers).json()['board']['ply'] == 1
    manager.engine.fail = False
    assert act(client, headers, 'reply', 1).json()['board']['ply'] == 2


@pytest.mark.parametrize('fen,move,termination', [
    ('4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1', 'e1g1', None),
    ('4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2', 'e5d6', None),
    ('7k/P7/8/8/8/8/8/4K3 w - - 0 1', 'a7a8q', None),
    ('7k/P7/8/8/8/8/8/4K3 w - - 0 1', 'a7a8n', 'insufficient_material'),
    ('7k/8/5KQ1/8/8/8/8/8 w - - 0 1', 'g6g7', 'checkmate'),
    ('7k/5K2/8/6Q1/8/8/8/8 w - - 0 1', 'g5g6', 'stalemate'),
])
def test_special_rules_are_shared(solo_client, fen, move, termination):
    client, manager = solo_client
    data, headers = begin(client)
    manager.get(data['token']).board = chess.Board(fen)
    data = act(client, headers, 'move', 0, move=move).json()
    assert data['board']['last_move'] == move
    assert data['board']['termination'] == termination
    assert data['summary']['reviewed_moves'] == 1


def test_capacity_expiry_and_concurrent_duplicate():
    async def run():
        manager = SoloManager(FakeEngine(), capacity=1, ttl=1)
        data = await manager.start(StartSolo())
        with pytest.raises(GameError, match='muitas partidas'):
            await manager.start(StartSolo())
        session = manager.get(data['token'])
        intent = SoloIntent(action='move', ply=0, move='e2e4')
        results = await asyncio.gather(manager.act(session, intent), manager.act(session, intent), return_exceptions=True)
        assert sum(isinstance(r, GameError) for r in results) == 1
        assert len(session.reviews) == 1 and session.board.ply() == 1
        session.last_activity -= 2
        manager.cleanup()
        assert not manager.sessions
    asyncio.run(run())


def test_missing_engine_and_close():
    async def run():
        engine = SoloEngine(path='/not/a/stockfish')
        with pytest.raises(GameError):
            await engine.candidates(chess.Board(), chess.WHITE)
        assert engine.failed and engine.engine is None
        await engine.close()
    asyncio.run(run())


@pytest.mark.parametrize('failure', ['timeout', 'crash', 'illegal'])
def test_strict_engine_failure_never_fakes_scores(monkeypatch, failure):
    async def run():
        closed = []
        class Transport:
            def close(self): closed.append(True)
        class Engine:
            async def configure(self, options): pass
            async def analyse(self, *args, **kwargs):
                if failure == 'timeout': await asyncio.sleep(10)
                if failure == 'crash': raise chess.engine.EngineTerminatedError('crash')
                return [{'pv': [chess.Move.from_uci('a1a8')], 'score': chess.engine.PovScore(chess.engine.Cp(0), chess.WHITE)}]
        async def launch(path): return Transport(), Engine()
        monkeypatch.setattr(chess.engine, 'popen_uci', launch)
        engine = SoloEngine(path='fake', timeout=.03)
        with pytest.raises(GameError): await engine.candidates(chess.Board(), chess.WHITE)
        assert closed and engine.failed
    asyncio.run(run())


def test_real_engine_levels_history_cache_and_full_game():
    if not LOCAL_ENGINE.is_file(): pytest.skip('Stockfish local não instalado')
    async def run():
        engine = SoloEngine(path=str(LOCAL_ENGINE))
        board = chess.Board()
        try:
            for difficulty in DIFFICULTIES:
                move = await engine.choose(board, difficulty, random.Random(4))
                assert move in board.legal_moves and board.fen() == chess.STARTING_FEN
            white = await engine.candidates(board, chess.WHITE)
            black = await engine.candidates(board, chess.BLACK)
            assert abs(white[0].cp + black[0].cp) < 70
            assert await engine.candidates(board, chess.WHITE) is white
            # A complete game starts normally and ends by resignation, through all real stages.
            manager = SoloManager(engine)
            data = await manager.start(StartSolo())
            session = manager.get(data['token'])
            for _ in range(6):
                own = (await engine.candidates(session.board, session.color))[0].move
                state = await manager.act(session, SoloIntent(action='move', ply=session.board.ply(), move=own.uci()))
                assert state['review']['comment'] and state['summary']['accuracy'] is not None
                if outcome(session.board): break
                await manager.act(session, SoloIntent(action='reply', ply=session.board.ply()))
            if not outcome(session.board):
                state = await manager.act(session, SoloIntent(action='resign', ply=session.board.ply(), confirmed=True))
            assert state['board']['status'] == 'finished'
            # Also finish by actual mate, not just resignation.
            session = Session(chess.WHITE, 'beginner', 'progressive', board=chess.Board('7k/8/5KQ1/8/8/8/8/8 w - - 0 1'))
            state = await manager.act(session, SoloIntent(action='move', ply=0, move='g6g7'))
            assert state['board']['termination'] == 'checkmate'
            assert state['review']['classification'] == 'excellent'
        finally:
            process = engine.engine
            await engine.close()
            assert engine.engine is None and engine.transport is None
            if process: assert process.returncode.done()
    asyncio.run(run())


def test_levels_select_different_candidates_and_review_stays_strong(monkeypatch):
    async def run():
        configs = []
        moves = list(chess.Board().legal_moves)[:8]
        class Transport:
            def close(self): pass
        class Engine:
            async def configure(self, options): configs.append(options)
            async def analyse(self, board, limit, multipv, **kwargs):
                return [{'pv': [move], 'score': chess.engine.PovScore(chess.engine.Cp(100-i*10), board.turn)} for i, move in enumerate(moves[:multipv])]
        async def launch(path): return Transport(), Engine()
        monkeypatch.setattr(chess.engine, 'popen_uci', launch)
        engine = SoloEngine(path='fake')
        weak = await engine.choose(chess.Board(), 'beginner', random.Random(0))
        hard = await engine.choose(chess.Board(), 'hard', random.Random(0))
        assert weak != hard and hard == moves[0]
        await engine.candidates(chess.Board(), chess.WHITE)
        assert configs[-1] == {'Skill Level': 20}
        await engine.close()
    asyncio.run(run())


def test_busy_solo_engine_preserves_health_and_cancellation_releases_lock(monkeypatch):
    async def run():
        engine = SoloEngine(path='fake')
        await engine.lock.acquire()
        try:
            with pytest.raises(GameError) as exc:
                await engine.candidates(chess.Board(), chess.WHITE)
            assert exc.value.code == 'ENGINE_BUSY' and not engine.failed
        finally: engine.lock.release()
        entered = asyncio.Event()
        class Transport:
            def close(self): pass
        class Engine:
            async def configure(self, options): pass
            async def analyse(self, *args, **kwargs):
                entered.set()
                await asyncio.sleep(30)
        async def launch(path): return Transport(), Engine()
        monkeypatch.setattr(chess.engine, 'popen_uci', launch)
        task = asyncio.create_task(engine.candidates(chess.Board(), chess.WHITE))
        await entered.wait()
        task.cancel()
        with pytest.raises(asyncio.CancelledError): await task
        assert not engine.lock.locked() and engine.engine is None
    asyncio.run(run())
