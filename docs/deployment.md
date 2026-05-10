# Deployment and Operations Guide

This document describes how to run the project locally and in a self-hosted environment.

## Prerequisites

- Python 3.12 and `uv` installed
- PostgreSQL 16
- Redis 7
- systemd (for optional service mode)

## Environment Variables

Use `.env` from `.env.example`.

Required minimum:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY` (replace in production)

Optional:

- `TEST_DATABASE_URL` (local tests)
- `WEBHOOK_SECRET` (for webhook validation)

## Local Run (development)

```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
bash scripts/run_api.sh
```

API:

- Swagger: `http://localhost:8000/docs`
- Health: `GET /api/v1/health`

## Services

- `scripts/run_api.sh` starts the API server
- `scripts/run_worker.sh` starts the worker process (`scheduled_posts` queue).
- `scripts/run_scheduler.sh` starts the periodic scheduler process.
- worker uses queue: `scheduled_posts` in Redis

## Production example (systemd)

- Keep the same command with Gunicorn:
  `uv run gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000`

- Run API, worker, scheduler as separate units from `docs/systemd/*.service`.

## Database and migrations

```bash
uv run alembic upgrade head
```
or

```bash
bash scripts/ensure_migrations.sh
```
For local SQLite recovery from legacy migration syntax, set:
```bash
AUTO_REPAIR_SQLITE=1 DATABASE_URL='sqlite+aiosqlite:///./dev.db' bash scripts/ensure_migrations.sh
```

Use a controlled backup strategy for PostgreSQL before upgrades.

## Backup checklist

- snapshot or dump database: `pg_dump -Fc rubika_bot`
- keep secrets in a dedicated secret store
- rotate deployment secrets periodically
