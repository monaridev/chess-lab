import chess
import pytest

from backend.hints import hint_messages
from tests.conftest import connected_pair, move_both, move_payload, new_pair


@pytest.mark.parametrize("fen,uci,expected", [
    ("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1", "e1g1", {"g1": "K", "f1": "R", "h1": None, "e1": None}),
    ("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1", "e8c8", {"c8": "k", "d8": "r", "a8": None, "e8": None}),
    ("4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2", "e5d6", {"d6": "P", "d5": None, "e5": None}),
])
def test_special_moves_broadcast_correct_position(client, manager, fen, uci, expected):
    white, black = new_pair(client)
    room = manager.get(white["code"])
    room.board = chess.Board(fen)
    with connected_pair(client, white, black) as (w, b):
        state = move_both(w, b, uci, room.board.turn)
        board = chess.Board(state["fen"])
        for square, symbol in expected.items():
            piece = board.piece_at(chess.parse_square(square))
            assert (piece.symbol() if piece else None) == symbol


@pytest.mark.parametrize("promotion", ["q", "r", "b", "n"])
@pytest.mark.parametrize("color", [True, False])
def test_all_promotions_both_colors(client, manager, promotion, color):
    white, black = new_pair(client)
    room = manager.get(white["code"])
    room.board = chess.Board("8/P6k/8/8/8/8/7p/4K3 w - - 0 1" if color else "8/P6k/8/8/8/8/7p/4K3 b - - 0 1")
    uci = ("a7a8" if color else "h2h1") + promotion
    with connected_pair(client, white, black) as (w, b):
        state = move_both(w, b, uci, color)
        assert chess.Board(state["fen"]).piece_at(chess.parse_square(uci[2:4])).symbol() == (promotion.upper() if color else promotion)


@pytest.mark.parametrize("fen,uci,code", [
    ("4k3/P7/8/8/8/8/8/4K3 w - - 0 1", "a7a8", "PROMOTION_REQUIRED"),
    ("k3r3/8/8/8/8/8/4R3/4K3 w - - 0 1", "e2f2", "KING_IN_CHECK"),
    ("k3r3/8/8/8/8/8/P7/4K3 w - - 0 1", "a2a3", "KING_IN_CHECK"),
    ("k4r2/8/8/8/8/8/8/4K2R w K - 0 1", "e1g1", "ILLEGAL_MOVE"),
    ("k3r3/8/8/3pP3/8/8/8/4K3 w - d6 0 1", "e5d6", "KING_IN_CHECK"),
])
def test_special_illegal_moves(client, manager, fen, uci, code):
    white, black = new_pair(client)
    room = manager.get(white["code"])
    room.board = chess.Board(fen)
    before = room.board.fen()
    with connected_pair(client, white, black) as (w, b):
        w.send_json(move_payload(uci))
        assert w.receive_json()["code"] == code
        assert room.board.fen() == before


def test_complete_game_checkmate_and_finished_rejection(client):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        move_both(w, b, "f2f3")
        move_both(w, b, "e7e5", False)
        move_both(w, b, "g2g4")
        state = move_both(w, b, "d8h4", False)
        assert state["check"] and state["check_square"] == "e1"
        assert state["status"] == "finished" and state["termination"] == "checkmate"
        assert state["result"] == "0-1" and state["winner"] == "black"
        assert state["legal_moves"] == []
        w.send_json(move_payload("a2a3"))
        assert w.receive_json()["code"] == "GAME_OVER"
        w.send_json({"type": "hint"})
        assert w.receive_json()["code"] == "GAME_OVER"
        w.send_json({"type": "reveal", "confirmed": True, "ply": 4})
        assert w.receive_json()["code"] == "GAME_OVER"


def test_check_and_legal_evasion(client, manager):
    white, black = new_pair(client)
    manager.get(white["code"]).board = chess.Board("4k3/8/8/8/8/8/8/R3K3 w - - 0 1")
    with connected_pair(client, white, black) as (w, b):
        state = move_both(w, b, "a1a8")
        assert state["check"] and state["status"] == "playing"
        state = move_both(w, b, "e8f7", False)
        assert not state["check"]


@pytest.mark.parametrize("fen,uci,termination", [
    ("7k/5K2/8/6Q1/8/8/8/8 w - - 0 1", "g5g6", "stalemate"),
    ("n6k/8/8/8/8/8/2b5/2K5 w - - 0 1", "c1c2", "insufficient_material"),
    ("7k/8/8/8/8/8/R7/K7 w - - 99 51", "a2b2", "fifty_moves"),
])
def test_draws_after_move(client, manager, fen, uci, termination):
    white, black = new_pair(client)
    manager.get(white["code"]).board = chess.Board(fen)
    with connected_pair(client, white, black) as (w, b):
        state = move_both(w, b, uci)
        assert state["termination"] == termination
        assert state["result"] == "1/2-1/2" and state["winner"] is None


def test_threefold_repetition_not_anticipated(client):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        for index, uci in enumerate(["g1f3", "g8f6", "f3g1", "f6g8"] * 2):
            state = move_both(w, b, uci, index % 2 == 0)
            assert state["status"] == ("finished" if index == 7 else "playing")
        assert state["termination"] == "threefold_repetition"


def test_hint_progression_private_legal_and_reset_for_both_players(client, manager):
    white, black = new_pair(client)
    room = manager.get(white["code"])
    with connected_pair(client, white, black) as (w, b):
        for level in [1, 2, 3, 4, 4]:
            w.send_json({"type": "hint"})
            hint = w.receive_json()
            assert hint["level"] == level and hint["type"] == "hint"
            assert "move" not in hint
            assert "san" not in hint
            assert room.board.fen() == chess.STARTING_FEN
        b.send_json({"type": "hint"})
        assert b.receive_json()["code"] == "NOT_YOUR_TURN"  # Nenhuma dica privada vazou.
        w.send_json({"type": "reveal", "confirmed": True, "ply": 0})
        revealed = w.receive_json()
        assert chess.Move.from_uci(revealed["move"]) in room.board.legal_moves
        assert revealed["type"] == "reveal"
        move_both(w, b, "e2e4")
        b.send_json({"type": "hint"})
        assert b.receive_json()["level"] == 1
        move_both(w, b, "e7e5", False)
        w.send_json({"type": "hint"})
        assert w.receive_json()["level"] == 1


def test_normal_mode_has_no_hints(client):
    white, black = new_pair(client, "normal")
    with connected_pair(client, white, black) as (w, b):
        w.send_json({"type": "hint"})
        assert w.receive_json()["code"] == "HINTS_DISABLED"
        move_both(w, b, "e2e4")


def test_reconnect_restores_only_already_revealed_hints(client):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        for level in (1, 2):
            w.send_json({"type": "hint"})
            hint = w.receive_json()
            assert len(hint["messages"]) == level
    with client.websocket_connect(f"/ws/{white['code']}") as w:
        w.send_json({"type": "auth", "token": white["player_token"]})
        assert w.receive_json()["type"] == "state"
        restored = w.receive_json()
        assert restored == hint and "move" not in restored
        w.send_json({"type": "hint"})
        assert w.receive_json()["level"] == 3


@pytest.mark.parametrize("fen", [chess.STARTING_FEN, "k3r3/8/8/8/8/8/4R3/4K3 w - - 0 1", "7k/5K2/8/6Q1/8/8/8/8 w - - 0 1", "4k3/P7/8/8/8/8/8/4K3 w - - 0 1"])
def test_hint_never_mutates_board_and_suggests_legal_move(fen):
    board = chess.Board(fen)
    before = board.fen()
    messages, uci = hint_messages(board)
    assert len(messages) == 4 and all(messages)
    assert chess.Move.from_uci(uci) in board.legal_moves
    assert board.fen() == before and not board.move_stack
    if board.is_check():
        assert "xeque" in messages[0]
