import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

import chess
import pytest
from starlette.websockets import WebSocketDisconnect

from backend.game import GameError
from backend.rooms import ALPHABET, RoomManager
from tests.conftest import connected_pair, move_both, move_payload, new_pair


def test_frontend_health_and_assets(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    page = client.get("/")
    assert page.status_code == 200
    assert "Chess Lab" in page.text and 'lang="pt-BR"' in page.text
    for asset in ("app.js", "styles.css", "favicon.svg", "pieces/white-k.svg", "pieces/black-q.svg"):
        assert client.get(f"/static/{asset}").status_code == 200
    assert page.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("mode", ["normal", "assisted"])
def test_room_creation_join_and_privacy(client, mode):
    result = client.post("/api/rooms", json={"mode": mode})
    assert result.status_code == 201
    white = result.json()
    assert white["color"] == "white" and white["mode"] == mode
    assert len(white["code"]) == 6 and set(white["code"]) <= set(ALPHABET)
    black = client.post(f"/api/rooms/{white['code'].lower()}/join").json()
    assert black["color"] == "black" and black["code"] == white["code"]
    assert black["player_token"] != white["player_token"]
    assert client.post(f"/api/rooms/{white['code']}/join").status_code == 409
    assert client.post("/api/rooms/NOPE99/join").status_code == 404
    with connected_pair(client, white, black) as (w, b):
        state = move_both(w, b, "e2e4")
        assert "token" not in str(state)
        assert state["turn"] == "black"


@pytest.mark.parametrize("body", [{"mode": "engine"}, {"mode": 1}, {"fen": chess.STARTING_FEN}, []])
def test_invalid_create_body(client, body):
    assert client.post("/api/rooms", json=body).status_code == 422


def test_waiting_and_second_player_broadcast(client):
    white = client.post("/api/rooms", json={}).json()
    with client.websocket_connect(f"/ws/{white['code']}") as w:
        w.send_json({"type": "auth", "token": white["player_token"]})
        state = w.receive_json()
        assert state["status"] == "waiting" and state["legal_moves"] == []
        w.send_json(move_payload("e2e4"))
        assert w.receive_json()["code"] == "WAITING_FOR_OPPONENT"
        w.send_json({"type": "hint"})
        assert w.receive_json()["code"] == "WAITING_FOR_OPPONENT"
        client.post(f"/api/rooms/{white['code']}/join")
        assert w.receive_json()["status"] == "playing"


@pytest.mark.parametrize("uci,color,code", [("e2e5", True, "ILLEGAL_MOVE"), ("e7e5", False, "NOT_YOUR_TURN"), ("e7e5", True, "OPPONENT_PIECE"), ("e3e4", True, "EMPTY_SQUARE")])
def test_rejected_move_preserves_state(client, manager, uci, color, code):
    white, black = new_pair(client)
    room = manager.get(white["code"])
    with connected_pair(client, white, black) as (w, b):
        sender = w if color else b
        sender.send_json(move_payload(uci))
        assert sender.receive_json()["code"] == code
        assert room.board.fen() == chess.STARTING_FEN
        assert not room.board.move_stack
        # Nenhum broadcast extra ou alteração de turno após erro.
        move_both(w, b, "e2e4")


@pytest.mark.parametrize("payload", ["not json", "[]", "null", '{"type":"move","from":"z9","to":"e4"}', '{"type":"move","from":"e2","to":"e4","fen":"fake"}', '{"type":"move","from":"e2","to":"e4","promotion":"k"}', '{"type":"hint","level":4}', '{"type":"reset"}', "x" * 4097])
def test_untrusted_messages_rejected(client, manager, payload):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        w.send_text(payload)
        assert w.receive_json()["code"] == "INVALID_MESSAGE"
        assert manager.get(white["code"]).board.fen() == chess.STARTING_FEN
        move_both(w, b, "e2e4")


def test_binary_message_rejected_connection_survives(client):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        w.send_bytes(b"binary")
        assert w.receive_json()["code"] == "INVALID_MESSAGE"
        move_both(w, b, "e2e4")


@pytest.mark.parametrize("token", ["x" * 43, "á" * 43, "short"])
def test_invalid_token(client, token):
    white, _ = new_pair(client)
    with client.websocket_connect(f"/ws/{white['code']}") as ws:
        ws.send_json({"type": "auth", "token": token})
        assert ws.receive_json()["code"] == "INVALID_TOKEN"
        with pytest.raises(WebSocketDisconnect):
            ws.receive_json()


def test_unknown_room_websocket(client):
    with client.websocket_connect("/ws/AAAAAA") as ws:
        assert ws.receive_json()["code"] == "ROOM_NOT_FOUND"


def test_disconnect_reconnect_retains_board_and_color(client):
    white, black = new_pair(client)
    with client.websocket_connect(f"/ws/{white['code']}") as w:
        w.send_json({"type": "auth", "token": white["player_token"]})
        w.receive_json()
        with client.websocket_connect(f"/ws/{black['code']}") as b:
            b.send_json({"type": "auth", "token": black["player_token"]})
            assert w.receive_json() == b.receive_json()
            played = move_both(w, b, "e2e4")
        offline = w.receive_json()
        assert not offline["players"]["black"]["connected"]
        assert offline["fen"] == played["fen"]
        with client.websocket_connect(f"/ws/{black['code']}") as reconnected:
            reconnected.send_json({"type": "auth", "token": black["player_token"]})
            state = reconnected.receive_json()
            assert state == w.receive_json()
            assert state["players"]["black"]["connected"]
            assert state["fen"] == played["fen"]
            move_both(w, reconnected, "e7e5", False)


def test_new_connection_replaces_old_without_erasing_presence(client):
    white, black = new_pair(client)
    with connected_pair(client, white, black) as (w, b):
        with client.websocket_connect(f"/ws/{white['code']}") as replacement:
            replacement.send_json({"type": "auth", "token": white["player_token"]})
            with pytest.raises(WebSocketDisconnect) as closed:
                w.receive_json()
            assert closed.value.code == 4001
            state = replacement.receive_json()
            assert state == b.receive_json()
            assert state["players"]["white"]["connected"]
            move_both(replacement, b, "e2e4")


def test_two_rooms_are_isolated(client, manager):
    pair_a, pair_b = new_pair(client), new_pair(client)
    with connected_pair(client, *pair_a) as (w, b):
        move_both(w, b, "d2d4")
    assert manager.get(pair_b[0]["code"]).board.fen() == chess.STARTING_FEN
    with client.websocket_connect(f"/ws/{pair_b[0]['code']}") as ws:
        ws.send_json({"type": "auth", "token": pair_a[0]["player_token"]})
        assert ws.receive_json()["code"] == "INVALID_TOKEN"


def test_competing_join_requests_assign_only_one_black(client):
    white = client.post("/api/rooms", json={}).json()
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(client.post, f"/api/rooms/{white['code']}/join") for _ in range(2)]
        assert sorted(f.result().status_code for f in futures) == [200, 409]


def test_disconnected_room_expiry_and_capacity():
    manager = RoomManager(ttl_seconds=10, max_rooms=1)
    room = manager.create("normal")
    with pytest.raises(GameError, match="cheio"):
        manager.create("normal")
    room.last_activity = time.monotonic() - 20
    room.connections[chess.WHITE] = object()
    manager.cleanup()
    assert room.code in manager.rooms
    room.connections.clear()
    manager.cleanup()
    with pytest.raises(GameError, match="não encontrada"):
        manager.get(room.code)
    assert manager.create("normal")


def test_failed_broadcast_disconnects_broken_socket_and_updates_other_player():
    class FakeSocket:
        def __init__(self, broken=False):
            self.broken = broken
            self.states = []
            self.close_code = None

        async def send_json(self, state):
            if self.broken:
                raise OSError("Conexão caiu")
            self.states.append(state)

        async def close(self, code):
            self.close_code = code

    manager = RoomManager()
    room = manager.create("normal")
    manager.join(room.code)
    white, black = FakeSocket(), FakeSocket(broken=True)
    room.connections = {chess.WHITE: white, chess.BLACK: black}
    asyncio.run(room.broadcast())
    assert black.close_code == 1011
    assert chess.BLACK not in room.connections
    assert not white.states[-1]["players"]["black"]["connected"]
    assert white.states[-1]["fen"] == chess.STARTING_FEN
