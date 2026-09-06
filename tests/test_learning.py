import chess
import pytest

from backend.learning import CHAPTERS, CATALOG, apply


def call(client, chapter, **body):
    return client.post(f"/api/learn/{chapter}", json=body)


def test_catalog_and_no_client_position(client):
    data = client.get('/api/learn').json()
    assert len(data) == 6
    assert sum(c['total'] for c in data) == 19
    assert call(client, 'missing').status_code == 400
    assert call(client, 'movimentos', fen=chess.STARTING_FEN).status_code == 422
    assert call(client, 'movimentos', moves=['bad']).status_code == 422
    assert call(client, 'movimentos', moves=['e2e4'] * 33).status_code == 422


@pytest.mark.parametrize('chapter', CHAPTERS, ids=lambda c: c.id)
def test_complete_chapter_replay_and_progressive_hints(client, chapter):
    moves = []
    for index, ex in enumerate(chapter.exercises):
        initial = call(client, chapter.id, moves=moves).json()
        assert initial['step'] == index
        assert initial['board']['fen'] == ex.fen
        assert not initial.get('reveal')
        for level in range(4):
            data = call(client, chapter.id, moves=moves, action='hint', level=level).json()
            assert data['level'] == level + 1
            assert len(data['hints']) == level + 1
            assert 'reveal' not in data and 'answers' not in data
            assert ex.answers[0] not in str(data['hints'])
        assert call(client, chapter.id, moves=moves, action='reveal', level=3).status_code == 400
        reveal = call(client, chapter.id, moves=moves, action='reveal', level=4).json()['reveal']
        assert reveal['move'] in ex.answers
        state = call(client, chapter.id, moves=moves, action='move', move=ex.answers[0]).json()
        moves.append(ex.answers[0])
        assert state['moves'] == moves
        assert state['after']['fen'] == apply(ex, moves[-1]).fen()
        assert state['feedback']
        assert call(client, chapter.id, moves=moves).json()['board'] == state['board']
    assert state['complete']
    assert call(client, chapter.id, moves=moves, action='move', move='e2e4').status_code == 400
    assert call(client, chapter.id, moves=moves).json()['complete']
    assert not call(client, chapter.id).json()['complete']


def test_rejection_is_atomic_and_independent_of_rooms(client, manager):
    start = call(client, 'movimentos').json()
    for uci, code in [('e2e5', 'ILLEGAL_MOVE'), ('e7e5', 'OPPONENT_PIECE'), ('e3e4', 'EMPTY_SQUARE'), ('a2a3', 'TRY_AGAIN')]:
        response = call(client, 'movimentos', action='move', move=uci)
        if code == 'TRY_AGAIN':
            assert response.status_code == 200
            assert response.json()['accepted'] is False
        else:
            assert response.status_code == 400
            assert response.json()['code'] == code
        assert call(client, 'movimentos').json() == start
    assert call(client, 'movimentos', moves=['a2a3']).status_code == 400
    room = client.post('/api/rooms', json={'mode': 'normal'}).json()
    call(client, 'movimentos', action='move', move='e2e4')
    assert manager.get(room['code']).board.fen() == chess.STARTING_FEN
    assert call(client, 'movimentos', action='move').status_code == 400


def test_curriculum_semantics_and_all_accepted_moves():
    for chapter in CHAPTERS:
        for ex in chapter.exercises:
            assert chess.Board(ex.fen).is_valid()
            for move in ex.answers:
                assert apply(ex, move).is_valid()
    assert chess.Board(CATALOG['xeque'].exercises[0].fen).is_check()
    mate = CATALOG['xeque'].exercises[1]
    assert all(apply(mate, move).is_checkmate() for move in mate.answers)
    castle = CATALOG['abertura'].exercises[-1]
    after = apply(castle, 'e1g1')
    assert after.piece_type_at(chess.G1) == chess.KING
    assert after.piece_type_at(chess.F1) == chess.ROOK
    fork = apply(CATALOG['ameacas'].exercises[0], 'e5f7')
    assert fork.is_check()
    assert chess.D8 in fork.attacks(chess.F7) and chess.H8 in fork.attacks(chess.F7)
    threat = apply(CATALOG['ameacas'].exercises[1], 'b1c3')
    assert chess.D5 in threat.attacks(chess.C3)
    assert not threat.is_attacked_by(chess.BLACK, chess.C3)
    guide = CATALOG['guiada']
    for i, ex in enumerate(guide.exercises):
        after = apply(ex, ex.answers[0])
        if i + 1 < len(guide.exercises):
            assert after.fen() == guide.exercises[i+1].fen
        else:
            assert after.is_checkmate()
