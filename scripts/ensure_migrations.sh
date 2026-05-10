#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
TMP_BOOTSTRAP_SCRIPT="$(mktemp)"
trap 'rm -f "$TMP_BOOTSTRAP_SCRIPT"' EXIT

if [[ -z "${DATABASE_URL:-}" ]]; then
  set -a
  [[ -f .env ]] && source ./.env
  set +a
fi

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is required for migration checks." >&2
  exit 1
fi

extract_sqlite_file() {
  local db_url=$1
  echo "${db_url#sqlite+aiosqlite:///}"
}

bootstrap_sqlite_from_models() {
  local db_url=$1
  local db_file
  db_file="$(extract_sqlite_file "$db_url")"

  if [[ "$db_file" == ":memory:" ]]; then
    echo "AUTO_REPAIR_SQLITE is not supported for in-memory SQLite URLs." >&2
    return 1
  fi

  rm -f "$db_file"

  cat <<'PY' > "$TMP_BOOTSTRAP_SCRIPT"
from sqlalchemy import create_engine
from app.db.base_class import Base
from app.models import *  # noqa: F401,F403
import os

db_url = os.environ["DATABASE_URL"]
sync_url = db_url.replace("+aiosqlite", "")
engine = create_engine(sync_url, future=True)
Base.metadata.create_all(engine)
PY
  DATABASE_URL="$db_url" uv run python "$TMP_BOOTSTRAP_SCRIPT"
}

echo "Checking migrations against: $DATABASE_URL"
echo "Current head(s):"
uv run alembic heads

echo "Applying migrations..."
set +e
LOG_FILE="$(mktemp)"
uv run alembic upgrade head 2>&1 | tee "$LOG_FILE"
STATUS=${PIPESTATUS[0]}
set -e

if [[ "$STATUS" -eq 0 ]]; then
  rm -f "$LOG_FILE"
  echo "Migrations applied successfully."
  exit 0
fi

if [[ "$DATABASE_URL" == sqlite* ]] && [[ "${DATABASE_URL}" == *"+aiosqlite://"* ]]; then
  if [[ "${AUTO_REPAIR_SQLITE:-0}" == "1" ]]; then
    bootstrap_sqlite_from_models "$DATABASE_URL"
    uv run alembic stamp head
    rm -f "$LOG_FILE"
    echo "SQLite failure handled by rebuilding from current SQLAlchemy models and stamping head."
    exit 0
  fi

  if grep -q "ALTER TABLE users ALTER COLUMN" "$LOG_FILE"; then
    echo "Known SQLite migration incompatibility detected: ALTER TABLE users ALTER COLUMN." >&2
    echo "Set AUTO_REPAIR_SQLITE=1 to allow local rebuild from current models."
    rm -f "$LOG_FILE"
    exit 1
  fi

  echo "SQLite migration failure persists. Set AUTO_REPAIR_SQLITE=1 to auto-rebuild local SQLite."
  rm -f "$LOG_FILE"
  exit 1
fi

echo "Migration failure persists. If this is a fresh PostgreSQL DB, this can be caused by legacy broken migration revision 7815ab12f360 and should be handled by either"
echo "  1) recreating the database from scratch, or"
echo "  2) restoring a DB already migrated past that revision, then running alembic upgrade head."
rm -f "$LOG_FILE"
exit "$STATUS"
