# System Architecture

## نمای کلی
سیستم از چند بخش اصلی تشکیل می‌شود:

1. Backend API
2. Database
3. Scheduler Worker
4. Message Processor
5. Reporting Layer

---

## اجزای اصلی

### 1. Backend API
وظایف:
- مدیریت کاربران
- مدیریت Workspace
- مدیریت کانال/گروه
- ثبت و ویرایش پست‌ها
- مدیریت قوانین پاسخ خودکار
- مدیریت قوانین فیلتر
- ارائه گزارش

### 2. Database
دیتابیس اصلی برای ذخیره:
- کاربران
- Workspaceها
- کانال‌ها و گروه‌ها
- پست‌های زمان‌بندی‌شده
- قوانین پاسخ خودکار
- قوانین فیلتر
- لاگ‌ها
- اشتراک‌ها

### 3. Scheduler Worker
وظایف:
- بررسی پست‌های زمان‌دار
- انتخاب پست‌های موعدرسیده
- ارسال به روبیکا
- ثبت نتیجه ارسال
- مدیریت خطا

### 4. Message Processor
وظایف:
- دریافت پیام‌های ورودی
- تشخیص مقصد
- اجرای فیلترها
- اجرای پاسخ خودکار
- ثبت لاگ‌ها

### 5. Reporting Layer
وظایف:
- استخراج آمار از لاگ‌ها
- ساخت گزارش روزانه/هفتگی
- ارائه خروجی قابل نمایش در پنل

---

## معماری منطقی
```text
Admin Panel / Bot Commands
|
v
Backend API
|
-------------------
|        |        |
v        v        v
Postgres   Redis   Rubika API
|
v
Workers / Processors

---

## معماری پردازش پیام

text
Incoming Message
|
v
Identify Channel/Group
|
v
Load Channel Rules
|
v
Run Filter Engine
|
  [If blocked => delete + log + stop]
|
v
Run Auto Reply Engine
|
  [If matched => reply + log]
|
v
End

---

## معماری زمان‌بندی پست

text
User creates scheduled post
|
v
Saved in DB with status=scheduled
|
v
Scheduler polls due posts
|
v
Lock post / set status=sending
|
v
Send via Rubika API
|
   -------------------
   |                 |
success            failed
   |                 |
   v                 v
status=sent      status=failed
log success      log failure

---

## پیشنهاد استقرار
### حالت ساده MVP
- یک سرور برای Backend API
- یک PostgreSQL
- یک Redis
- یک Worker Process

### حالت توسعه‌یافته
- Backend API مستقل
- Worker مستقل
- Message Processor مستقل
- Reverse Proxy
- Monitoring

---

## اصول معماری
- ماژولار بودن
- جداسازی API از Job Processing
- ثبت لاگ برای عملیات کلیدی
- سادگی در MVP
- قابلیت توسعه در فازهای بعد


---
