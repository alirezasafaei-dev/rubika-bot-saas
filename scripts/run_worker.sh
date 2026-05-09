#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f app/workers/__init__.py ]]; then
  echo "Worker package not initialized yet."
  echo "Create worker entrypoint before enabling this script."
  exit 1
fi

if [[ ! -f app/workers/runner.py ]]; then
  echo "Worker runner not found at app/workers/runner.py"
  echo "Add worker bootstrap before enabling this script."
  exit 1
fi

echo "Starting worker (placeholder entrypoint)."
uv run python -m app.workers.runner
