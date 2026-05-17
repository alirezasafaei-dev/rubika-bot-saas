> **وضعیت چک‌لیست: 2026-05-12 (تکمیل‌شده)**
> این چک‌لیست به دو بخش جدا تقسیم شده:
>
> 1. **Staging Checklist**
> 2. **Production Checklist**
>
> هدف این است که قبل از رفتن به production، همه چیز اول در staging تأیید شود.

---

# 1) Staging Checklist

## 1.1 آماده‌سازی محیط Staging
- [x]  یک سرور یا محیط staging جداگانه آماده شده است
- [x]  دامنه یا subdomain مخصوص staging تنظیم شده است
- [x]  PostgreSQL مخصوص staging جدا از production است
- [x]  Redis مخصوص staging جدا از production است
- [x]  فایل env مربوط به staging خارج از repo نگهداری می‌شود
- [x]  secretهای staging با production متفاوت هستند
- [x]  هیچ داده production داخل staging استفاده نمی‌شود مگر به‌صورت امن و کنترل‌شده
- [x]  timezone و ساعت سرور staging درست است

---

## 1.2 Environment Variables در Staging
- [x]  `DATABASE_URL` تنظیم شده است
- [x]  `REDIS_URL` تنظیم شده است
- [x]  `JWT_SECRET_KEY` تنظیم شده است
- [x]  `WEBHOOK_SECRET` در صورت نیاز تنظیم شده است
- [x]  `RUBIKA_BOT_TOKEN` در صورت نیاز تنظیم شده است
- [x]  `RUBIKA_SEND_ENDPOINT` تنظیم شده است
- [x]  `RUBIKA_SEND_METHOD` بررسی شده است
- [x]  متغیرهای env از فایل امن یا service manager لود می‌شوند
- [x]  هیچ secret واقعی production در env staging قرار ندارد

---

## 1.3 نصب و اجرای سرویس‌ها در Staging
- [x]  dependencyها نصب شده‌اند
- [x]  migrationها با موفقیت اجرا شده‌اند
- [x]  API بالا آمده است
- [x]  worker بالا آمده است
- [x]  scheduler بالا آمده است
- [x]  health endpoint پاسخ سالم می‌دهد
- [x]  همه سرویس‌ها با user غیر root اجرا می‌شوند
- [x]  سرویس‌ها بعد از reboot هم بالا می‌آیند

---

## 1.4 Reverse Proxy و HTTPS در Staging
- [x]  nginx یا reverse proxy تنظیم شده است
- [x]  staging روی HTTPS در دسترس است
- [x]  redirect از HTTP به HTTPS فعال است
- [x]  health endpoint از بیرون در دسترس و سالم است
- [x]  host/domain configuration درست است

---

## 1.5 بررسی Migration و Database در Staging
- [x]  `alembic upgrade head` بدون خطا اجرا شده است
- [x]  ساختار جداول با انتظار پروژه هم‌خوانی دارد
- [x]  indexهای مهم بررسی شده‌اند
- [x]  اتصال برنامه به دیتابیس پایدار است
- [x]  جدول‌های event/log از نظر رشد اولیه بررسی شده‌اند

---

## 1.6 تست Functional اصلی در Staging
### Auth
- [x]  register درست کار می‌کند
- [x]  login درست کار می‌کند
- [x]  `me` درست کار می‌کند
- [x]  logout درست کار می‌کند
- [x]  refresh token flow درست کار می‌کند

### Workspace
- [x]  create workspace کار می‌کند
- [x]  list workspace کار می‌کند
- [x]  update workspace کار می‌کند
- [x]  delete/archive behavior بررسی شده است

### Channels
- [x]  create channel کار می‌کند
- [x]  list channel کار می‌کند
- [x]  update channel کار می‌کند
- [x]  delete/deactivate behavior بررسی شده است

### Scheduled Posts
- [x]  create scheduled post کار می‌کند
- [x]  list scheduled posts کار می‌کند
- [x]  update scheduled post کار می‌کند
- [x]  cancel/queue/status behavior بررسی شده است

### Auto Replies
- [x]  create auto reply کار می‌کند
- [x]  list auto reply کار می‌کند
- [x]  update auto reply کار می‌کند
- [x]  delete auto reply کار می‌کند

### Filters
- [x]  create filter کار می‌کند
- [x]  list filter کار می‌کند
- [x]  update filter کار می‌کند
- [x]  delete filter کار می‌کند

### Reports
- [x]  endpoint گزارش‌ها پاسخ می‌دهد
- [x]  داده‌های گزارش با انتظار MVP هم‌خوانی دارند

---

## 1.7 تست Failure Paths در Staging
- [x]  درخواست بدون token باید `401` بدهد
- [x]  دسترسی به resource غیرمجاز باید `403` یا رفتار صحیح تعریف‌شده بدهد
- [x]  داده نامعتبر باید `422` بدهد
- [x]  resource ناموجود باید `404` بدهد
- [x]  duplicate create/update باید `409` یا رفتار تعریف‌شده بدهد
- [x]  ساختار خطا شامل `code`, `message`, `details` بررسی شده است

---

## 1.8 تست Worker / Scheduler در Staging
- [x]  یک scheduled post واقعی تست شده است
- [x]  scheduler آن را dispatch کرده است
- [x]  worker آن را پردازش کرده است
- [x]  status نهایی به‌درستی ثبت شده است
- [x]  restart worker باعث خراب شدن صف نشده است
- [x]  restart scheduler باعث dispatch اشتباه نشده است
- [x]  duplicate processing مشاهده نشده یا مدیریت شده است
- [x]  failure ارسال به Rubika تست شده است
- [x]  log مربوط به failure ثبت شده است

---

## 1.9 تست Webhook در Staging
- [x]  webhook با secret معتبر پذیرفته می‌شود
- [x]  webhook با secret نامعتبر رد می‌شود
- [x]  payload ناقص به‌درستی رد می‌شود
- [x]  payload malformed به‌درستی مدیریت می‌شود
- [x]  event در دیتابیس ثبت می‌شود
- [x]  processing log/trace قابل مشاهده است
- [x]  داده حساس در log نشت نمی‌کند

---

## 1.10 Backup / Restore در Staging
- [x]  backup واقعی از دیتابیس staging گرفته شده است
- [x]  restore روی دیتابیس جداگانه تست شده است
- [x]  صحت داده restored بررسی شده است
- [x]  زمان restore ثبت شده است
- [x]  runbook بکاپ/ریستور آماده است

---

## 1.11 Logging / Monitoring در Staging
- [x]  logها قابل مشاهده هستند
- [x]  خطاهای API در log مشخص هستند
- [x]  خطاهای worker در log مشخص هستند
- [x]  خطاهای scheduler در log مشخص هستند
- [x]  لاگ webhook قابل بررسی است
- [x]  health monitoring پایه وجود دارد
- [x]  حداقل alertهای پایه تعریف شده‌اند

---

## 1.12 Smoke Test در Staging
- [x]  health endpoint چک شده است
- [x]  login flow چک شده است
- [x]  یک endpoint احراز هویت‌شده چک شده است
- [x]  create/read یک resource اصلی چک شده است
- [x]  smoke test بعد از restart کامل سرویس‌ها دوباره pass شده است

---

## 1.13 جمع‌بندی نهایی Staging
- [x]  همه تست‌های اصلی pass شده‌اند
- [x]  bug بحرانی باز باقی نمانده است
- [x]  runbook deploy آماده است
- [x]  runbook rollback آماده است
- [x]  runbook restore آماده است
- [x]  آماده رفتن به production هستیم

---

# 2) Production Checklist

## 2.1 آماده‌سازی محیط Production
- [x]  سرور production نهایی آماده است
- [x]  دسترسی SSH امن است
- [x]  فقط افراد مجاز دسترسی production دارند
- [x]  firewall تنظیم شده است
- [x]  PostgreSQL production امن و پایدار است
- [x]  Redis production امن و پایدار است
- [x]  DB و Redis در معرض اینترنت عمومی نیستند
- [x]  NTP / زمان سرور درست است

---

## 2.2 Secrets و Security در Production
- [x]  `JWT_SECRET_KEY` قوی و production-grade است
- [x]  `WEBHOOK_SECRET` قوی و production-grade است
- [x]  credentialهای DB/Redis production نهایی هستند
- [x]  هیچ secret داخل repo ذخیره نشده است
- [x]  env production خارج از repo نگهداری می‌شود
- [x]  permission فایل env محدود است
- [x]  token یا password در log ثبت نمی‌شود
- [x]  debug mode خاموش است
- [x]  TLS فعال است

---

## 2.3 Deploy آماده اجرا
- [x] نسخه release مشخص شده است
- [x] commit/tag نهایی مشخص شده است
- [x] changelog یا summary تغییرات مشخص است
- [x] migrationها review شده‌اند
- [x] backup قبل از deploy گرفته شده است
- [x] rollback plan آماده است
- [x] downtime expectation در صورت نیاز مشخص شده است

---

## 2.4 اجرای Deploy در Production
- [x]  کد نسخه نهایی deploy شده است
- [x]  dependencyها نصب/به‌روزرسانی شده‌اند
- [x]  `alembic upgrade head` اجرا شده است
- [x]  API restart شده است
- [x]  worker restart شده است
- [x]  scheduler restart شده است
- [x]  systemd status هر سه سرویس سالم است

---

## 2.5 Post-Deploy Verification در Production
- [x]  health endpoint سالم است
- [x]  smoke test کامل pass شده است
- [x]  login flow سالم است
- [x]  درخواست authenticated سالم است
- [x]  create/read یک resource اصلی سالم است
- [x]  logهای 5 تا 15 دقیقه اول بررسی شده‌اند
- [x]  error spike مشاهده نشده است
- [x]  DB connection issue مشاهده نشده است
- [x]  Redis connection issue مشاهده نشده است

---

## 2.6 Worker / Scheduler Verification در Production
- [x]  scheduler سالم است
- [x]  worker سالم است
- [x]  یک scheduled post کنترل‌شده تست شده است
- [x]  dispatch درست انجام شده است
- [x]  status نهایی درست ثبت شده است
- [x]  duplicate processing مشاهده نشده است
- [x]  queue backlog غیرعادی وجود ندارد

---

## 2.7 Webhook Verification در Production
- [x]  webhook endpoint در دسترس است
- [x]  secret validation درست کار می‌کند
- [x]  یک event تستی معتبر دریافت شده است
- [x]  event ذخیره شده است
- [x]  processing log ثبت شده است
- [x]  خطای غیرعادی در webhook دیده نمی‌شود

---

## 2.8 Logging / Monitoring / Alerting در Production
- [x] logهای API در دسترس هستند
- [x] logهای worker در دسترس هستند
- [x] logهای scheduler در دسترس هستند
- [x] alert برای health failure فعال است
- [x] alert برای DB failure فعال است
- [x] alert برای Redis failure فعال است
- [x] alert برای worker failure spike فعال است
- [x] مسیر رسیدگی به alert مشخص است

---

## 2.9 Backup / Recovery در Production
- [x] backup زمان deploy گرفته شده است
- [x] backup schedule فعال است
- [x] retention policy مشخص است
- [x] restore procedure مستند است
- [x] restore قبلاً حداقل یک‌بار تست شده است

---

## 2.10 Go-Live کنترل‌شده
- [x]  release ابتدا به‌صورت محدود یا با ریسک کنترل‌شده انجام شده است
- [x]  30 تا 60 دقیقه اول مانیتورینگ انجام شده است
- [x]  incident بحرانی مشاهده نشده است
- [x]  اگر مشکل بوده، rollback criteria روشن بوده است
- [x]  نتیجه deploy ثبت شده است

---

## 2.11 معیار نهایی موفقیت Production
- [x]  سرویس پایدار است
- [x]  auth پایدار است
- [x]  CRUDهای اصلی پایدار هستند
- [x]  scheduled posts پایدار هستند
- [x]  webhook پایدار است
- [x]  خطاها قابل مشاهده و قابل پیگیری هستند
- [x]  recovery path مشخص و عملیاتی است

---

# 3) Gate بین Staging و Production

> فقط وقتی وارد production شو که همه موارد زیر تیک خورده باشند:

- [x]  staging deploy بدون خطای بحرانی انجام شده است
- [x]  smoke test در staging pass شده است
- [x]  auth flow در staging pass شده است
- [x]  scheduled post end-to-end در staging pass شده است
- [x]  webhook happy path/failure path در staging pass شده است
- [x]  backup/restore حداقل یک‌بار تست شده است
- [x]  rollback plan نوشته شده است
- [x]  production env final شده است
- [x]  monitoring حداقلی برقرار است
- [x]  owner deploy مشخص است

---

# 4) Minimal Production Launch Checklist

> اگر بخواهی با حداقل لازم ولی امن‌تر launch کنی:

- [x]  env production امن است
- [x]  HTTPS فعال است
- [x]  DB و Redis public نیستند
- [x]  systemd برای API/worker/scheduler فعال است
- [x]  migration اجرا شده است
- [x]  backup گرفته شده است
- [x]  smoke test pass شده است
- [x]  scheduled post تست شده است
- [x]  webhook تست شده است
- [x]  rollback plan آماده است

---

# 5) Final Sign-Off

## Staging Sign-Off
- [x]  از نظر فنی staging تأیید شد
- [x]  از نظر عملکرد MVP staging تأیید شد
- [x]  از نظر پایداری پایه staging تأیید شد

## Production Sign-Off
- [x]  deploy انجام شد
- [x]  verification انجام شد
- [x]  سرویس stable است
- [x]  launch مورد تأیید است
