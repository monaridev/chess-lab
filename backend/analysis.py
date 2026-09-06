"""Análise opcional, assíncrona e limitada; nunca recebe o tabuleiro oficial."""

import asyncio
import logging
import os
import shutil
from contextlib import suppress
from collections import OrderedDict
from pathlib import Path

import chess
import chess.engine

from .hints import HintPlan, build_plan

log = logging.getLogger(__name__)
LOCAL_ENGINE = Path(__file__).resolve().parent.parent / ".tools/stockfish/stockfish"


class AnalysisService:
    def __init__(self, path: str | None = None, time_limit: float = 0.25,
                 depth: int = 14, timeout: float = 2.0, cache_size: int = 128):
        configured = path if path is not None else os.getenv("STOCKFISH_PATH")
        self.path = configured if configured is not None else (str(LOCAL_ENGINE) if LOCAL_ENGINE.is_file() else shutil.which("stockfish"))
        self.time_limit = max(0.01, min(time_limit, 1.0))
        self.depth = max(1, min(depth, 20))
        self.timeout = timeout
        self.cache_size = cache_size
        self.cache: OrderedDict[str, HintPlan] = OrderedDict()
        self.lock = asyncio.Lock()
        self.transport = None
        self.engine = None
        self.failed = False

    async def start(self):
        if not self.engine:
            self.transport, self.engine = await chess.engine.popen_uci(self.path)
            await self.engine.configure({"Threads": 1, "Hash": 32})

    async def _analyse(self, board: chess.Board) -> chess.Move | None:
        await self.start()
        candidates = await self.engine.analyse(
            board, chess.engine.Limit(time=self.time_limit, depth=self.depth),
            multipv=3, info=chess.engine.INFO_SCORE | chess.engine.INFO_PV,
        )
        # A engine oferece evidência; apenas candidatos legais são aceitos.
        for candidate in candidates:
            pv = candidate.get("pv", [])
            if pv and pv[0] in board.legal_moves:
                return pv[0]
        return None

    async def plan(self, position: chess.Board) -> HintPlan:
        board = position.copy(stack=True)
        key = board.fen()
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        move = None
        if self.path and not self.failed:
            acquired = False
            try:
                # Fila curta: sobrecarga usa heurísticas, sem prender outras salas.
                await asyncio.wait_for(self.lock.acquire(), timeout=0.5)
                acquired = True
                if not self.failed:
                    move = await asyncio.wait_for(self._analyse(board), timeout=self.timeout)
            except TimeoutError:
                if acquired:
                    self.failed = True
                    await self.close()
            except (OSError, chess.engine.EngineError, ValueError):
                self.failed = True
                await self.close()
                log.warning("Stockfish indisponível; dicas continuam com heurísticas locais.")
            except asyncio.CancelledError:
                if acquired:
                    await self.close()
                raise
            finally:
                if acquired:
                    self.lock.release()
        # Até o fallback roda fora do event loop.
        plan = await asyncio.to_thread(build_plan, board, move, "stockfish" if move else "heuristic")
        self.cache[key] = plan
        self.cache.move_to_end(key)
        while len(self.cache) > self.cache_size:
            self.cache.popitem(last=False)
        return plan

    async def close(self):
        engine = self.engine
        if self.transport:
            self.transport.close()
        self.transport = None
        self.engine = None
        if engine and getattr(engine, "returncode", None) is not None:
            with suppress(TimeoutError):
                await asyncio.wait_for(asyncio.shield(engine.returncode), timeout=1)
