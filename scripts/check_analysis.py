"""Smoke da engine/fallback no mesmo runtime usado pelo servidor."""
import argparse
import asyncio
import chess
from backend.analysis import AnalysisService

async def check(expected):
    service = AnalysisService()
    try:
        board = chess.Board()
        plan = await service.plan(board)
        assert plan.source == expected, (plan.source, expected)
        assert chess.Move.from_uci(plan.move) in board.legal_moves
        assert len(plan.messages) == 4
        print(f"OK: análise {expected}, lance legal e quatro pistas.")
    finally:
        await service.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected', choices=['stockfish', 'heuristic'], required=True)
    asyncio.run(check(parser.parse_args().expected))
