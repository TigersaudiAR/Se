#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACK_PID=""
FRONT_PID=""

cleanup() {
  if [[ -n "$FRONT_PID" ]]; then
    kill "$FRONT_PID" 2>/dev/null || true
  fi
  if [[ -n "$BACK_PID" ]]; then
    kill "$BACK_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

(
  cd "$BACKEND_DIR"
  poetry install
  poetry run uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
) &
BACK_PID=$!

echo "Backend started with PID $BACK_PID"

sleep 2

(
  cd "$FRONTEND_DIR"
  npm install
  npm run dev -- --host 127.0.0.1 --port 5173
) &
FRONT_PID=$!

echo "Frontend started with PID $FRONT_PID"

sleep 3
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://127.0.0.1:5173" >/dev/null 2>&1 || true
elif command -v open >/dev/null 2>&1; then
  open "http://127.0.0.1:5173" >/dev/null 2>&1 || true
fi

echo "TwoCards dev stack running at http://127.0.0.1:5173"

wait $FRONT_PID
