#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set; loading .env if present."
  set -a
  # shellcheck source=/dev/null
  [[ -f .env ]] && . ./.env
  set +a
fi

echo "Starting FastAPI app at 0.0.0.0:8000"
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
