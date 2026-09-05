"""Dois clientes contra um servidor existente, inclusive pelo IP da rede local.

Uso: .venv/bin/python -m tests.smoke_network --url http://192.168.15.3:8000
"""

import argparse
import asyncio
import json

import httpx
from websockets.asyncio.client import connect


async def receive(ws):
    return json.loads(await asyncio.wait_for(ws.recv(), 5))


async def authenticate(ws, player):
    await ws.send(json.dumps({"type": "auth", "token": player["player_token"]}))
    return await receive(ws)


async def smoke(url):
    async with httpx.AsyncClient(base_url=url, trust_env=False) as http:
        response = await http.get("/api/health")
        response.raise_for_status()
        response = await http.post("/api/rooms", json={"mode": "assisted"})
        response.raise_for_status()
        white = response.json()
        response = await http.post(f"/api/rooms/{white['code']}/join")
        response.raise_for_status()
        black = response.json()
    ws_url = url.replace("http://", "ws://", 1).replace("https://", "wss://", 1).rstrip("/") + f"/ws/{white['code']}"
    async with connect(ws_url, proxy=None) as w:
        await authenticate(w, white)
        async with connect(ws_url, proxy=None) as b:
            assert await authenticate(b, black) == await receive(w)
            for level in range(1, 5):
                await w.send(json.dumps({"type": "hint"}))
                assert (await receive(w))["level"] == level
            await w.send(json.dumps({"type": "reveal", "confirmed": True, "ply": 0}))
            assert (await receive(w))["type"] == "reveal"
            await w.send(json.dumps({"type": "move", "from": "e2", "to": "e5"}))
            assert (await receive(w))["code"] == "ILLEGAL_MOVE"
            await b.send(json.dumps({"type": "move", "from": "e7", "to": "e5"}))
            assert (await receive(b))["code"] == "NOT_YOUR_TURN"
            await w.send(json.dumps({"type": "move", "from": "f2", "to": "f3"}))
            state = await receive(w)
            assert state == await receive(b)
        assert not (await receive(w))["players"]["black"]["connected"]
        async with connect(ws_url, proxy=None) as b:
            resumed = await authenticate(b, black)
            assert resumed == await receive(w) and resumed["fen"] == state["fen"]
            for ws, uci in [(b, "e7e5"), (w, "g2g4"), (b, "d8h4")]:
                await ws.send(json.dumps({"type": "move", "from": uci[:2], "to": uci[2:]}))
                state = await receive(w)
                assert state == await receive(b)
            assert state["termination"] == "checkmate" and state["result"] == "0-1"
    print("OK: HTTP, sala, dois WebSockets, dicas, revelação, rejeições, sincronização, reconexão e xeque-mate.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    asyncio.run(smoke(parser.parse_args().url))
