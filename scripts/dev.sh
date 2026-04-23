#!/usr/bin/env bash
# Starts backend, frontend, and Electron for local development.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

echo "[1/3] Backend  → http://127.0.0.1:8000"
( cd backend && python -m uvicorn app.main:app --reload --port 8000 ) &
BACK_PID=$!
trap "kill $BACK_PID 2>/dev/null || true" EXIT

echo "[2/3] Frontend → http://127.0.0.1:5173"
( cd frontend && npm run dev ) &
FRONT_PID=$!
trap "kill $BACK_PID $FRONT_PID 2>/dev/null || true" EXIT

sleep 3

echo "[3/3] Electron shell"
( cd electron && ACCOTECH_SKIP_BACKEND=1 npm start )
