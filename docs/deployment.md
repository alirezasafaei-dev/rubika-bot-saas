# Deployment and Operations Guide

This document describes how to run the project locally and in a self-hosted environment.

## Prerequisites

- Python 3.12 and `uv` installed
- PostgreSQL 16
- Redis 7
- systemd (for optional service mode)

## Environment Variables

Use `.env` from `.env.example`.

Reference details:

- `docs/environment-reference.md`
- `docs/customer-deployment-template.md`
- `docs/customer-handover-checklist.md`

Required minimum:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY` (replace in production)

Optional:

- `TEST_DATABASE_URL` (local tests)
- `WEBHOOK_SECRET` (for webhook validation)
- `RUBIKA_BOT_TOKEN` (for scheduled posts sending)
- `RUBIKA_SEND_ENDPOINT` (default: `https://botapi.rubika.ir/v3/{TOKEN}/{METHOD}`)
- `RUBIKA_SEND_METHOD` (default: `sendMessage`)
- `SCHEDULER_INTERVAL_SECONDS` (default: `30`)
- `SCHEDULER_BATCH_SIZE` (default: `100`)

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

### Rubika webhook registration (production)

- Register webhook endpoint with Rubika using `updateBotEndpoints`:
  - `url`: `https://rbsaas.alirezasafaeisystems.ir/api/v1/webhooks/rubika`
  - `type`: `ReceiveUpdate`
  - `secret`: optional, from `WEBHOOK_SECRET`

```bash
cd /home/deploy/rubika-bot-saas
export DOMAIN_FOR_RUBIKABOTSAAS=https://rbsaas.alirezasafaeisystems.ir/
export WEBHOOK_SECRET=... # optional
bash scripts/configure_rubika_webhook.sh
```

Expected success response:
`{\"status\":\"OK\",\"data\":{\"status\":\"Done\"}}` or equivalent positive status.

## Reverse proxy (nginx) on VPS

- Server block added for:
  - `rbsaas.alirezasafaeisystems.ir` on port `80` -> `127.0.0.1:8000`.
- Quick proxy smoke test:
  - `curl -H "Host: rbsaas.alirezasafaeisystems.ir" http://127.0.0.1/api/v1/health`

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

## Out-of-repo tasks (operator checklist)

- After deployment, do the Rubika-side tasks in:
  - `docs/rubika-external-operations.md`
- Quick confirm on Rubika-side before announcing production:
  - Bot token is valid and stored in env only (not in repo)
  - Webhook registered and accepted (`status: Done`)
  - Bot is member/admin where scheduling needs to send messages

## Production maintenance runbook

- Keep a short daily maintenance log in this repo:
  - `docs/production-maintenance-log.md`
- Run these commands for quick operational verification:
  - `curl -H "Host: rbsaas.alirezasafaeisystems.ir" https://rbsaas.alirezasafaeisystems.ir/api/v1/health`
  - `systemctl is-active rubika-api.service rubika-worker.service rubika-scheduler.service`
  - `cd /home/deploy/rubika-bot-saas && source .venv/bin/activate && alembic current`
- Optional log storage cleanup (server side):
  - `sudo journalctl --vacuum-size=1G`
- Check storage usage:
  - `df -h / /home`
  - `du -h /home/deploy/rubika-bot-saas | sort -rh | head -n 20`
