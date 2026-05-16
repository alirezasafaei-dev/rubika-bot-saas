#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
UV_BIN="uv"
if command -v uv >/dev/null 2>&1; then
  UV_BIN="uv"
elif [ -x "${REPO_ROOT}/.venv/bin/uv" ]; then
  UV_BIN="${REPO_ROOT}/.venv/bin/uv"
elif [ -x "${REPO_ROOT}/.venv/bin/python" ]; then
  UV_BIN="${REPO_ROOT}/.venv/bin/python -m"
else
  UV_BIN="python -m"
fi

if [[ ! -f app/workers/__init__.py ]]; then
  echo "Missing app/workers package."
  exit 1
fi

if [[ ! -f app/workers/runner.py ]]; then
  echo "Missing app/workers/runner.py."
  exit 1
fi

echo "Starting worker."
if [[ "$UV_BIN" == *" -m" ]]; then
  ${UV_BIN} app.workers.runner
else
  ${UV_BIN} run python -m app.workers.runner
fi
