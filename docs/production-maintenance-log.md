# Production Maintenance Log

Date: 2026-05-17

## Current stabilization tasks completed

- Production services validated and active:
  - `rubika-api.service`
  - `rubika-worker.service`
  - `rubika-scheduler.service`
- Health endpoint confirmed: `GET /api/v1/health` returns `{"status":"ok"}`
- Webhook registration confirmed using `scripts/configure_rubika_webhook.sh` and got:
  - `{"status":"OK","data":{"status":"Done"}}`

## Storage / runtime cleanup

- Disk usage before cleanup (server `185.3.124.93`): `/` at `57%` (32G used / 59G).
- Project directory size: `330M` (including venv).
- `systemd` journal cleanup executed:
  - `sudo journalctl --vacuum-size=1G`
  - reduced archived journal usage from `1.9G` to about `1.0G`.

## Operational notes

- Active process list for scheduler/worker is controlled by systemd (no extra detached duplicates observed):
  - `uv run python -m app.scheduler.runner`
  - `uv run python -m app.workers.runner`
  - each has one child `python3 -m ...` process.
- DB tables present in current production schema:
  - `scheduled_posts`
  - `webhook_events`
  - `message_processing_logs`
  - `webhooks`, `webhook_deliveries`
  - `users`, `channels`, `workspace_members`, etc.
- Data sanity checks performed (counts sampled):
  - `scheduled_posts`: 7
  - `webhook_events`: 0
  - `workspace_members`: 13
  - `users`: 17
  - `channels`: 10

## Planned cleanup / future maintenance

- Keep periodic checks:
  - `curl -H "Host: rbsaas.alirezasafaeisystems.ir" https://rbsaas.alirezasafaeisystems.ir/api/v1/health`
  - `systemctl is-active rubika-api.service rubika-worker.service rubika-scheduler.service`
  - `alembic current`
- Optional periodic cleanup:
  - `sudo journalctl --vacuum-time=30d` (or size-based vacuum)
  - remove orphaned venv caches only if explicitly needed and after backup
