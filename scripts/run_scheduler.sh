#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
UV_BIN="uv"
if ! command -v uv >/dev/null 2>&1 && [ -x "${REPO_ROOT}/.venv/bin/uv" ]; then
  UV_BIN="${REPO_ROOT}/.venv/bin/uv"
fi

if [[ ! -f app/scheduler/__init__.py ]]; then
  echo "Missing app/scheduler package."
  exit 1
fi

if [[ ! -f app/scheduler/runner.py ]]; then
  echo "Missing app/scheduler/runner.py."
  exit 1
fi

echo "Starting scheduler runner."
${UV_BIN} run python -m app.scheduler.runner
