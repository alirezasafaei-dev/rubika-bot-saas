# A05 Customer Deployment Template

## Goal

Repeatable deployment for one customer environment with minimal ad-hoc decisions.

## Standard Layout

- App directory: `/home/deploy/rubika-bot-saas`
- Env file: `/home/deploy/rubika-bot-saas/.env`
- Services:
  - `rubika-api.service`
  - `rubika-worker.service`
  - `rubika-scheduler.service`

## Pre-Deploy Checklist

- Server access confirmed
- Domain and DNS confirmed
- PostgreSQL and Redis reachable
- Production secrets collected
- Backup point created before migration or upgrade

## Deployment Steps

1. Copy repository to target server
2. Create or update `.env` from `.env.example`
3. Install dependencies with `uv sync`
4. Run migrations with `uv run alembic upgrade head`
5. Install or update systemd unit files from `docs/systemd/`
6. Restart API, worker, and scheduler
7. Register or confirm Rubika webhook
8. Run health and auth smoke checks

## Verify Commands

```bash
curl -fsS https://<domain>/api/v1/health
systemctl is-active rubika-api.service rubika-worker.service rubika-scheduler.service
cd /home/deploy/rubika-bot-saas && uv run alembic current
```

## Customer-Specific Mapping

| Item | Example | Owner |
| --- | --- | --- |
| Domain | `rbsaas.example.com` | Customer |
| API port | `8000` | Delivery team |
| PostgreSQL DB | `rubika_bot` | Joint |
| Redis DB | `redis://localhost:6379/0` | Joint |
| Bot token | Stored in `.env` only | Customer |

## Rollback Trigger

Rollback if migrations fail, services do not stay active, or webhook verification fails after deployment.
