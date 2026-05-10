#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f app/workers/__init__.py ]]; then
  echo "Missing app/workers package."
  exit 1
fi

if [[ ! -f app/workers/runner.py ]]; then
  echo "Missing app/workers/runner.py."
  exit 1
fi

echo "Starting worker."
uv run python -m app.workers.runner
