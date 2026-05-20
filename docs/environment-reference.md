# A05 Environment Reference

## Core App

| Variable | Required | Purpose |
| --- | --- | --- |
| `APP_NAME` | No | Display name for the API |
| `VERSION` | No | App version string |
| `API_V1_STR` | No | API prefix, default `/api/v1` |
| `DEBUG` | No | Enables docs and debug-friendly behavior |
| `ENVIRONMENT` | Yes | `development`, `staging`, or `production` |

## Database and Queue

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | Yes | Async SQLAlchemy database connection |
| `SYNC_DATABASE_URL` | Yes | Sync database connection used by migrations and admin tasks |
| `TEST_DATABASE_URL` | No | Test-only SQLite URL for local pytest runs |
| `REDIS_URL` | Yes | Redis connection for queueing and scheduling |

## Auth and Webhooks

| Variable | Required | Purpose |
| --- | --- | --- |
| `JWT_SECRET_KEY` | Yes | Secret for signing access and refresh tokens |
| `JWT_ALGORITHM` | No | JWT signing algorithm, default `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | No | Access token TTL in minutes |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | No | Refresh token TTL in days |
| `WEBHOOK_SECRET` | No | Optional shared secret for webhook validation |

## Rubika Integration

| Variable | Required | Purpose |
| --- | --- | --- |
| `RUBIKA_BOT_NAME` | No | Internal operator label |
| `RUBIKA_BOT_USERNAME` | No | Bot username for reference |
| `RUBIKA_BOT_TOKEN` | Yes for live sending | Rubika bot access token |
| `RUBIKA_SEND_ENDPOINT` | No | Send API endpoint template |
| `RUBIKA_SEND_METHOD` | No | Default send method, usually `sendMessage` |
| `RUBIKA_SEND_TIMEOUT_SECONDS` | No | Send request timeout |

## Scheduler Controls

| Variable | Required | Purpose |
| --- | --- | --- |
| `SCHEDULER_INTERVAL_SECONDS` | No | How often the scheduler scans due work |
| `SCHEDULER_BATCH_SIZE` | No | Max due jobs handled per scheduler cycle |

## Production Rules

- Use unique production values for `JWT_SECRET_KEY` and `RUBIKA_BOT_TOKEN`
- Keep `.env` outside version control and rotate secrets after operator changes
- Use production-safe database URLs, not local defaults
- Keep `DEBUG=false` in production
