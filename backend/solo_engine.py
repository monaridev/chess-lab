"""Strict local UCI analysis for Solo; lifecycle shared with assisted analysis."""
import asyncio
import random
from dataclasses import dataclass

import chess
import chess.engine

from .analysis import AnalysisService
from .game import GameError, outcome


@dataclass(frozen=True)
class Candidate:
    move: chess.Move | None
    cp: int  # Always from the requested player's point of view.
    mate: int | None = None
    pv: tuple[chess.Move, ...] = ()


# skill, seconds, depth, MultiPV, acceptable concession, candidate weights
DIFFICULTIES = {
    "beginner": (0, .08, 6, 8, 280, (1, 2, 3, 4, 5, 6, 7, 8)),
    "easy": (4, .12, 9, 5, 150, (5, 4, 3, 2, 1)),
    "medium": (10, .20, 12, 3, 60, (8, 2, 1)),
    "hard": (20, .35, 16, 1, 0, (1,)),
}


class SoloEngine(AnalysisService):
    async def candidates(self, position, color, *, opponent=None):
        board = position.copy(stack=True)
        result = outcome(board)
        if result:
            score = 0 if result.winner is None else (10000 if result.winner == color else -10000)
            return [Candidate(None, score, 0 if result.winner is not None else None)]
        if not self.path or self.failed:
            raise GameError("ENGINE_UNAVAILABLE", "Stockfish local indisponível. Configure STOCKFISH_PATH e reinicie o servidor. Os outros modos continuam disponíveis.")
        skill, seconds, depth, count = DIFFICULTIES[opponent][:4] if opponent else (20, .25, 14, 3)
        # Include history: identical FENs may have different repetition outcomes.
        key = (board.fen(), tuple(m.uci() for m in board.move_stack), color)
        if not opponent and key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        acquired = False
        try:
            await asyncio.wait_for(self.lock.acquire(), .5)
            acquired = True
            async def run():
                await self.start()
                await self.engine.configure({"Skill Level": skill})
                infos = await self.engine.analyse(board, chess.engine.Limit(time=seconds, depth=depth),
                                                  multipv=count, info=chess.engine.INFO_SCORE | chess.engine.INFO_PV)
                candidates = []
                for info in infos:
                    pv = info.get("pv", [])
                    if pv and pv[0] in board.legal_moves and "score" in info:
                        score = info["score"].pov(color)
                        candidates.append(Candidate(pv[0], score.score(mate_score=10000), score.mate(), tuple(pv)))
                if not candidates:
                    raise ValueError("No legal scored candidate")
                return candidates
            candidates = await asyncio.wait_for(run(), self.timeout)
        except TimeoutError:
            if acquired:
                self.failed = True
                await self.close()
            raise GameError("ENGINE_BUSY", "A análise local demorou. Tente novamente; se persistir, reinicie o servidor.")
        except (OSError, ValueError, chess.engine.EngineError):
            self.failed = True
            await self.close()
            raise GameError("ENGINE_UNAVAILABLE", "Não foi possível analisar com Stockfish local. Reinicie o servidor após conferir o binário.")
        except asyncio.CancelledError:
            if acquired:
                await self.close()
            raise
        finally:
            if acquired:
                self.lock.release()
        if not opponent:
            self.cache[key] = candidates
            while len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)
        return candidates

    async def choose(self, board, difficulty, rng=None):
        candidates = await self.candidates(board, board.turn, opponent=difficulty)
        best = max(c.cp for c in candidates)
        budget, weights = DIFFICULTIES[difficulty][4:]
        eligible = [(c, weights[i]) for i, c in enumerate(candidates) if best - c.cp <= budget]
        return (rng or random).choices([c.move for c, _ in eligible], weights=[w for _, w in eligible])[0]
