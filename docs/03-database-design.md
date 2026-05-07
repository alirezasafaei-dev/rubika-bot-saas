# Database Design

## انتخاب دیتابیس
پیشنهاد اصلی: PostgreSQL

دلایل:
- پایداری بالا
- پشتیبانی خوب از JSONB
- مناسب برای گزارش‌گیری
- عملکرد مناسب در پروژه‌های SaaS

---

## موجودیت‌های اصلی

### 1. users
اطلاعات کاربران سیستم

### 2. workspaces
فضای کاری هر مشتری

### 3. workspace_members
اعضای Workspace

### 4. channels
کانال‌ها و گروه‌های متصل

### 5. scheduled_posts
پست‌های زمان‌بندی‌شده

### 6. post_logs
لاگ ارسال پست

### 7. auto_reply_rules
قوانین پاسخ خودکار

### 8. auto_reply_keywords
کلیدواژه‌های هر قانون

### 9. auto_reply_logs
لاگ اجرای پاسخ خودکار

### 10. filter_rules
قوانین فیلتر

### 11. moderation_logs
لاگ حذف و مدیریت محتوا

### 12. activity_logs
رویدادهای عمومی سیستم

### 13. subscriptions
پلن و وضعیت اشتراک

---

## روابط اصلی

- هر `user` می‌تواند چند `workspace` داشته باشد
- هر `workspace` چند `channel` دارد
- هر `channel` می‌تواند چند:
  - `scheduled_post`
  - `auto_reply_rule`
  - `filter_rule`
  داشته باشد

- هر `scheduled_post` چند `post_log` می‌تواند داشته باشد
- هر `auto_reply_rule` چند `keyword` دارد
- اجرای فیلتر و پاسخ خودکار در لاگ‌های جدا ذخیره می‌شود

---

## نکات طراحی
- حذف Cascade فقط در موجودیت‌هایی استفاده شود که حذف آن‌ها منطقی است
- برای داده‌های عملیاتی، ترجیحاً از `status` استفاده شود
- برای گزارش‌ها از جداول لاگ استفاده شود
- `JSONB` فقط برای داده‌های کم‌ساختار استفاده شود
- ایندکس روی فیلدهای پرتکرار جست‌وجو ضروری است

---

## وضعیت‌های مهم

### وضعیت کانال
- `active`
- `inactive`
- `disconnected`

### وضعیت پست
- `draft`
- `scheduled`
- `sending`
- `sent`
- `failed`
- `cancelled`

### وضعیت اشتراک
- `active`
- `expired`
- `cancelled`

---

## نکات گزارش‌گیری
گزارش‌ها از این جداول ساخته می‌شوند:
- `scheduled_posts`
- `post_logs`
- `auto_reply_logs`
- `moderation_logs`
- `activity_logs`
