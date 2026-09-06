"""Run with .venv/bin/python -m tests.smoke_solo; real full game, no network."""
import asyncio
import json
from pathlib import Path
import random
import socket

from backend.solo import SoloIntent, SoloManager, StartSolo


async def main():
    # Local UCI subprocesses are allowed; Internet connections fail this smoke test.
    original = socket.socket.connect
    def local_only(sock, address):
        if sock.family in (socket.AF_INET, socket.AF_INET6):
            if address[0] not in ('127.0.0.1', '::1'):
                raise AssertionError(f'Unexpected network connection: {address}')
        return original(sock, address)
    socket.socket.connect = local_only
    random.seed(18)
    manager = SoloManager()
    moves = []
    try:
        data = await manager.start(StartSolo(difficulty='beginner'))
        session = manager.get(data['token'])
        for _ in range(400):
            if data['board']['status'] == 'finished': break
            if session.board.turn == session.color:
                best = (await manager.engine.candidates(session.board, session.color))[0].move
                data = await manager.act(session, SoloIntent(action='move', ply=session.board.ply(), move=best.uci()))
                assert data['review']['comment'] and data['summary']['reviewed_moves'] == len(session.reviews)
            else:
                data = await manager.act(session, SoloIntent(action='reply', ply=session.board.ply()))
            moves.append(session.board.peek().uci())
        assert data['board']['status'] == 'finished', 'No natural ending within 400 plies'
        report = {'result': data['board']['result'], 'termination': data['board']['termination'],
                  'plies': len(moves), 'moves': moves, 'summary': data['summary'], 'reviews': data['history'], 'external_network': 'blocked'}
        path = Path('artifacts/solo-full-game.json')
        path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(json.dumps({k: v for k, v in report.items() if k not in ('moves', 'reviews')}, ensure_ascii=False))
    finally:
        socket.socket.connect = original
        await manager.engine.close()


if __name__ == '__main__':
    asyncio.run(main())
