"""As pistas usam evidência concreta sem vazar o destino da revelação."""
import chess
import pytest
from backend.hints import build_plan


@pytest.mark.parametrize('fen,uci,expected', [
    ('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1', 'c7c5', ('controlar d4', 'disputar o centro')),
    (chess.STARTING_FEN, 'g1f3', ('4 peças menores', 'd4', 'e5')),
    ('rnbqkb1r/pppppppp/5n2/8/8/5N2/PPPPPPPP/RNBQKB1R w KQkq - 2 2', 'b1c3', ('3 peças menores', 'd5', 'e4')),
    ('4k3/8/2p5/3p4/4P3/8/8/4K3 w - - 0 1', 'e4d5', ('captura de peão', '1 defensor direto', 'recapturar legalmente')),
    ('5r2/7k/8/8/8/2B5/8/4K3 w - - 0 1', 'c3b4', ('Torre em f8', 'contra-atacar')),
])
def test_evidence_is_position_specific_and_destination_stays_private(fen, uci, expected):
    board = chess.Board(fen)
    before = board.fen()
    plan = build_plan(board, chess.Move.from_uci(uci), 'stockfish')
    text = ' '.join(plan.messages)
    assert all(fragment in text for fragment in expected)
    assert uci not in text and uci[2:4] not in text
    assert plan.move == uci and plan.san == board.san(chess.Move.from_uci(uci))
    assert board.fen() == before
    assert 'outras jogadas podem existir' in plan.explanation


def test_capture_explanation_names_actual_piece_and_square():
    board = chess.Board('4k3/8/8/3r4/4P3/8/8/4K3 w - - 0 1')
    plan = build_plan(board, chess.Move.from_uci('e4d5'))
    assert 'peão captura a torre em d5' in plan.explanation
    assert 'd5' not in ' '.join(plan.messages)
