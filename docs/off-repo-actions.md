# خارج از مخزن لازم است انجام شود

این موارد در محیط local ریپو انجام می‌شوند، اما در یک محیط production/remote لازم است خارج از این کد انجام شوند:

- ایجاد سرویس PostgreSQL و Redis با شناسه‌های واقعی و تنظیمات محیطی:
  - `DATABASE_URL`
  - `REDIS_URL`
- اجرای مایگریشن دیتابیس:
  - `uv run alembic upgrade head`
  - اگر محیطی از تاریخچه‌ی migration معیوب `7815ab12f360_add_scheduled_posts_table` برخورد، ابتدا دیتابیس را با مهاجرت تمیز (schema جدید) بازسازی کنید یا تصمیم عملیات رفع خطا را پیش از اجرای `upgrade` هماهنگ کنید.
- مقداردهی secret ها در محیط اجرا:
  - `SECRET_KEY`/`JWT_SECRET_KEY`
  - `WEBHOOK_SECRET` (در صورت نیاز)
- راه‌اندازی سرویس API:
  - `uv run uvicorn app.main:app --host 0.0.0.0 --port 8000`
- اجرای worker و scheduler
- تنظیم reverse proxy (Nginx/Traefik) و TLS
- تنظیم backup برای دیتابیس PostgreSQL
- افزودن دامنه/سی‌دی‌ان و deployment manifest نهایی در محیط شما
