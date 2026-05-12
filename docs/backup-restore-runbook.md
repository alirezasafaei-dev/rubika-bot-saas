# Backup & Restore Runbook

## Backup

- **Script:** `/home/deploy/rubika-bot-saas/scripts/backup.sh`
- **Schedule:** `0 */6 * * *` (every 6 hours) via deploy user crontab
- **Retention:** auto-cleanup files older than 14 days in `/home/deploy/rubika-bot-saas/backups`
- **Outputs:**
  - `rubika_bot_<YYYYMMDD-HHMMSS>.dump`
  - `rubika_bot_redis_<YYYYMMDD-HHMMSS>.rdb`
- **Log:** `/home/deploy/rubika-bot-saas/logs/backup.log`

## Pre-deploy backup

- Before production deploy, run once manually:
  - `/home/deploy/rubika-bot-saas/scripts/backup.sh`
- Keep newest backup copy before release for rollback.

## Restore test procedure

1. Pick latest backup file: `ls -t /home/deploy/rubika-bot-saas/backups/rubika_bot_*.dump | head -n 1`
2. Create temp DB and restore:
   - `createdb -T template0 rubika_bot_restore_test`
   - `pg_restore -h 127.0.0.1 -p 5432 -U rubika_user -d rubika_bot_restore_test <dump_file>`
3. Smoke check in restored DB:
   - `psql -d rubika_bot_restore_test -c "SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename='users';"`
4. Drop temp DB:
   - `dropdb rubika_bot_restore_test`

## Alerting and escalation

- **Monitor script:** `/home/deploy/rubika-bot-saas/scripts/monitor.sh`
- **Cron:** `*/5 * * * * /home/deploy/rubika-bot-saas/scripts/monitor.sh`
- **Checks:** health endpoint, DB, Redis, worker, scheduler, queue spike
- **Targets:** append to `/home/deploy/rubika-bot-saas/logs/monitor.log` and `syslog` tag `rubika-bot-saas-monitor`
