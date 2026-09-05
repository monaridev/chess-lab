#!/bin/sh
set -eu
# exec entrega SIGTERM diretamente ao Uvicorn; nunca usar múltiplos workers.
exec python -m uvicorn backend.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1 --ws-max-size 4096 --timeout-graceful-shutdown 15
