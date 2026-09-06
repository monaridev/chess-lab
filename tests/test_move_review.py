import chess
import pytest

from backend.move_review import accuracy, adjusted_loss, classify, review_move, summary
from backend.solo_engine import Candidate


def review(fen, uci, before_cp=0, after_cp=0, best_mate=None, after_mate=None, reply=None):
    before = chess.Board(fen)
    move = chess.Move.from_uci(uci)
    assert move in before.legal_moves
    after = before.copy(); after.push(move)
    candidates = [Candidate(move, before_cp, best_mate)]
    played = Candidate(chess.Move.from_uci(reply) if reply else None, after_cp, after_mate,
                       (chess.Move.from_uci(reply),) if reply else ())
    return review_move(before, move, after, candidates, played)


@pytest.mark.parametrize('loss,expected', [(0,'excellent'), (20,'very_good'), (50,'good'), (110,'inaccuracy'), (200,'mistake'), (500,'blunder')])
def test_classification_calibration(loss, expected):
    assert classify(loss) == expected


def test_context_and_rare_brilliant():
    assert classify(80, tactical=True) == 'interesting'
    assert classify(800, forced=True) == 'excellent'
    assert classify(0, mate_lost=True) == 'blunder'
    assert classify(0, allows_mate=True) == 'blunder'
    assert classify(0, unique=True, tactical=True, sacrifice=True) == 'brilliant'
    for args in ({'unique': True}, {'tactical': True, 'sacrifice': True}, {'unique': True, 'tactical': True}):
        assert classify(0, **args) == 'excellent'
    assert classify(adjusted_loss(-1600, -2100)) != 'blunder'


@pytest.mark.parametrize('fen,uci,concept,word', [
    (chess.STARTING_FEN, 'g1f3', 'desenvolvimento', 'cavalo'),
    (chess.STARTING_FEN, 'e2e4', 'centro', 'e4'),
    ('4k3/8/8/8/8/8/8/R3K2R w KQ - 0 1', 'e1g1', 'roque', 'roque'),
    ('7k/8/8/8/8/8/1b6/R3K3 w - - 0 1', 'a1b1', 'peça salva', 'torre'),
    ('3k3r/8/8/4N3/8/8/8/4K3 w - - 0 1', 'e5f7', 'garfo', 'rei'),
    ('4k3/8/2n5/8/8/8/8/4KB2 w - - 0 1', 'f1b5', 'cravada', 'c6'),
    ('7k/8/8/8/q7/8/8/R3K3 w - - 0 1', 'a1a4', 'captura', 'dama'),
    ('7k/P7/8/8/8/8/8/4K3 w - - 0 1', 'a7a8q', 'promoção', 'dama'),
    ('7k/8/5KQ1/8/8/8/8/8 w - - 0 1', 'g6g7', 'mate encontrado', 'mate'),
])
def test_real_semantic_facts_are_specific_short_and_deterministic(fen, uci, concept, word):
    result = review(fen, uci)
    assert concept in result['concepts']
    assert word in result['comment']
    assert len(result['comment']) < 220
    assert result == review(fen, uci)


def test_hanging_and_ignored_threat_override_positional_praise():
    fen = '7k/8/8/8/8/8/1b6/RN2K3 w - - 0 1'
    result = review(fen, 'b1c3', 0, -240, reply='b2a1')
    assert result['classification'] == 'mistake'
    assert 'ameaça ignorada' in result['concepts']
    assert 'torre em a1' in result['comment']
    assert 'desenvolveu' not in result['comment']


def test_mate_lost_and_allowed_take_priority():
    lost = review('7k/8/5KQ1/8/8/8/8/8 w - - 0 1', 'g6b1', 9999, 900, best_mate=1)
    assert lost['classification'] == 'blunder' and 'mate' in lost['comment']
    board = chess.Board()
    for uci in ['f2f3', 'e7e5']: board.push_uci(uci)
    allowed = review(board.fen(), 'g2g4', -100, -9999, after_mate=-1, reply='d8h4')
    assert allowed['classification'] == 'blunder'
    assert 'mate contra seu rei' in allowed['comment']


def test_correct_sacrifice_is_not_penalized_by_material_alone():
    # Rook is offered to the bishop, but the supplied engine evaluation verifies compensation.
    result = review('7k/8/8/8/8/8/1b6/R3K3 w - - 0 1', 'e1f1', 0, 0)
    assert result['classification'] == 'excellent'
    assert result['loss'] == 0
    assert not any(e['negative'] for e in result['evidence'])


def test_accuracy_is_bounded_monotonic_and_not_rating():
    clean = [{'loss': 0}] * 10
    assert accuracy([]) is None
    assert accuracy(clean) == 100
    assert accuracy([{'loss': 15}] * 10) > 90
    assert accuracy(clean + [{'loss': 600}]) < 92
    assert accuracy([{'loss': 500}] * 10) < accuracy([{'loss': 100}] * 10)
    assert 0 <= accuracy([{'loss': 1200}]) <= 100
    assert adjusted_loss(-1200, -1800) < adjusted_loss(0, -600)
    assert adjusted_loss(100, -500) == 600
    assert adjusted_loss(-500, 100) == 0


def test_summary_counts_only_reviewed_player_moves():
    reviews = [review(chess.STARTING_FEN, 'g1f3'), review(chess.STARTING_FEN, 'e2e4', 20, -180)]
    value = summary(reviews)
    assert sum(value['counts'].values()) == 2
    assert 'desenvolvimento' in value['strengths']
    assert value['counts']['Erro'] == 1


def test_only_legal_move_is_marked_forced_without_noise_penalty():
    result = review('7k/5K2/8/8/8/8/8/6R1 b - - 0 1', 'h8h7', -700, -900)
    assert result['is_forced'] and result['classification'] == 'excellent'
    assert result['loss'] == 0
