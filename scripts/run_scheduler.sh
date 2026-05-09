#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f app/scheduler/__init__.py ]]; then
  echo "Scheduler package not initialized yet."
  echo "Create scheduler bootstrap before enabling this script."
  exit 1
fi

if [[ ! -f app/scheduler/runner.py ]]; then
  echo "Scheduler runner not found at app/scheduler/runner.py"
  echo "Add scheduler boot process before enabling this script."
  exit 1
fi

echo "Starting scheduler (placeholder entrypoint)."
uv run python -m app.scheduler.runner
