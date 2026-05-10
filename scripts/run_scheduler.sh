#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f app/scheduler/__init__.py ]]; then
  echo "Missing app/scheduler package."
  exit 1
fi

if [[ ! -f app/scheduler/runner.py ]]; then
  echo "Missing app/scheduler/runner.py."
  exit 1
fi

echo "Starting scheduler runner."
uv run python -m app.scheduler.runner
