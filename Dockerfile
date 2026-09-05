FROM python:3.12-slim-bookworm@sha256:782412e85d0f0984994c290652577d4018aff08145c85b262bb63dc0c7522254

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STOCKFISH_PATH=/usr/games/stockfish

# Pacote Debian inclui engine, rede NNUE e licença, sem binário local no Git.
RUN apt-get update \
    && apt-get install -y --no-install-recommends stockfish=15.1-4 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 chesslab
WORKDIR /app
COPY requirements.lock ./
RUN python -m pip install --no-cache-dir -r requirements.lock
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY --chmod=755 scripts/start.sh ./scripts/start.sh
COPY scripts/check_analysis.py ./scripts/check_analysis.py
USER chesslab
CMD ["/bin/sh", "scripts/start.sh"]
