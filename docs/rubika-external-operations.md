# Rubika External Operations Checklist (Out of Project Scope)

این کارها بیرون از کد پروژه‌اند و باید توسط شما در پنل/کنسول Rubika انجام شوند.

## 1) Bot setup
- Bot را در Rubika ایجاد/بررسی کن و `TOKEN` نهایی را داشته باش.
- `RUBIKA_BOT_TOKEN` را فقط در secret env روی سرور قرار بده (داخل repo ننویس).
- اگر ارسال پیام استفاده می‌کنی، مطمئن شو bot در حالت فعّال است و روی اکانت صحیح ثبت شده است.

## 2) Webhook registration
- در سرور backend دامنه production را تنظیم کن:
  - `DOMAIN_FOR_RUBIKABOTSAAS=https://rbsaas.alirezasafaeisystems.ir`
- سپس روی سرور اجرا کن:
  - `bash scripts/configure_rubika_webhook.sh`
- خروجی موفق مورد قبول:
  - `{"status":"OK","data":{"status":"Done"}}`
- اگر Rubika فقط با HTTP/HTTPS خاصی کار می‌کند، همان را تنظیم کن و دوباره ثبت کن.

## 3) کانال / گروه Rubika
- Rubika channel/group را بساز یا شناسایی کن.
- `rubika_channel_id` واقعی باید از رویداد واقعی Rubika بدست بیاید (مثلاً `g0...`).
- ID کانال را در API خودت از مسیر `channels` وارد کن.
- در صورت نیاز bot را ادمین کانال/گروه کن تا ارسال پیام مجاز باشد.

## 4) تست اتصال رویدادها (manual)
- یک پیام تستی به bot بفرست تا رویداد webhook در `webhook_events` ثبت شود.
- مسیر API:
  - `GET /api/v1/webhooks/rubika` (فقط برای health/webhook endpoint check با POST)
- تأیید در اپ:
  - `webhook_events`/`webhooks` در DB باید log داشته باشند.
  - endpoint health سالم باشد و `webhook` خطای 405 برای `HEAD`/`GET` نداشته باشد.

## 5) امنیت و دسترسی
- Secret webhook را اگر فعال کردی، در request header/format مطابق مستندات Rubika نگه دار.
- Secret و token ها را rotate کن (حداقل هر چند ماه یک‌بار).
- webhook secret را در `.env` واقعی نگه دار، نه داخل git.

## 6) تنظیمات نهایی برای production واقعی
- DNS/SSL دامنه را نهایی کن (در حال حاضر `https://rbsaas.alirezasafaeisystems.ir`).
- مطمئن شو مسیر `POST /api/v1/webhooks/rubika` همیشه دسترس‌پذیر و 200/expected روی payload درست باشد.
- اگر پیام‌ها ارسال نمی‌شوند:
  - بررسی کن bot در Rubika admin/permissions هست.
  - بررسی کن `RUBIKA_SEND_METHOD` و endpoint send صحیح است.
  - log worker و scheduler را برای خطاهای `scheduled post` چک کن.

## 7) نقاطی که هر 7 روز چک کن
- webhook still registered
- one scheduled post test (send and dispatch)
- last 200 logs in API/worker/scheduler
- certificate validity and DNS
