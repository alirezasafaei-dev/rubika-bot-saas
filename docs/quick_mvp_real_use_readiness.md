# وضعیت آماده‌سازی سریع MVP (کم‌مصرف)

تاریخ: 2026-05-10

## وضعیت آپدیت شده
- `ruff` ✅
- `mypy` ✅
- `pytest` ✅ (38 passed)
- `DATABASE_URL` واقعی شما در `Docker/محیط محلی` روی PostgreSQL با `uv run alembic upgrade head` بررسی شد و با موفقیت اجرا می‌شود.
- migrationهای بحرانی مربوط به `scheduled_posts` و `webhook logs` اصلاح شدند.
- worker برای scheduled posts الان مسیر integration جداگانه برای Rubika دارد و در صورت ست بودن endpoint/token می‌تواند ارسال واقعی انجام دهد.

## نکات فعلی برای محیط واقعی
1. `RUBIKA_SEND_ENDPOINT`، `RUBIKA_SEND_METHOD` و `RUBIKA_SEND_TIMEOUT_SECONDS` در `.env` پروژه تنظیم شد.
2. اگر `RUBIKA_BOT_TOKEN`/endpoint واقعی ست نباشد، سیستم به‌صورت ایمن no-op می‌ماند (برای جلوگیری از شکست تست).
3. برای استفاده production لازم است endpoint و اعتبارنامه معتبر روبیکا در سرور نیز در `.env` موجود باشد.

## فایل‌های تغییرکرده
- `app/core/config.py`
- `app/workers/jobs.py`
- `app/integrations/rubika_sender.py` (جدید)
- `alembic/versions/7815ab12f360_add_scheduled_posts_table.py`
- `alembic/versions/1b4fdbf2f3a7_add_webhook_event_processing_logs.py`
- `docs/deployment.md`
- `.env.example`
- `.env`
- `docs/quick_mvp_real_use_readiness.md`
