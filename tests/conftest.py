from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient

from backend.main import create_app
from backend.analysis import AnalysisService
from backend.rooms import RoomManager


@pytest.fixture
def manager():
    return RoomManager()


@pytest.fixture
def client(manager):
    with TestClient(create_app(manager, AnalysisService(path=""))) as test_client:
        yield test_client


def new_pair(client, mode="assisted"):
    white = client.post("/api/rooms", json={"mode": mode}).json()
    black = client.post(f"/api/rooms/{white['code']}/join").json()
    return white, black


@contextmanager
def connected_pair(client, white, black):
    with client.websocket_connect(f"/ws/{white['code']}") as w:
        w.send_json({"type": "auth", "token": white["player_token"]})
        assert w.receive_json()["type"] == "state"
        with client.websocket_connect(f"/ws/{black['code']}") as b:
            b.send_json({"type": "auth", "token": black["player_token"]})
            assert w.receive_json() == b.receive_json()
            yield w, b


def move_payload(uci):
    return {"type": "move", "from": uci[:2], "to": uci[2:4], "promotion": uci[4:] or None}


def move_both(w, b, uci, color=True):
    (w if color else b).send_json(move_payload(uci))
    state = w.receive_json()
    assert state["type"] == "state"
    assert state == b.receive_json()
    assert state["last_move"] == uci
    return state
