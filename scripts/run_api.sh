#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
UV_BIN="uv"
if ! command -v uv >/dev/null 2>&1 && [ -x "${REPO_ROOT}/.venv/bin/uv" ]; then
  UV_BIN="${REPO_ROOT}/.venv/bin/uv"
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is not set; loading .env if present."
  set -a
  # shellcheck source=/dev/null
  [[ -f .env ]] && . ./.env
  set +a
fi

UVICORN_ARGS=(app.main:app --host 0.0.0.0 --port 8000)
if [[ "${ENVIRONMENT:-development}" == "development" || "${DEBUG:-false}" == "true" ]]; then
  UVICORN_ARGS+=(--reload)
fi

echo "Starting FastAPI app at 0.0.0.0:8000"
${UV_BIN} run uvicorn "${UVICORN_ARGS[@]}"
