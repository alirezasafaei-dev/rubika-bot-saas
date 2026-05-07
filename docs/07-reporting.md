# Reporting

## هدف
ارائه گزارش ساده و قابل اتکا برای MVP.

## شاخص‌های گزارش

### گزارش پست‌ها
- تعداد پست‌های ایجادشده
- تعداد پست‌های زمان‌بندی‌شده
- تعداد پست‌های ارسال‌شده
- تعداد پست‌های ناموفق

### گزارش پاسخ خودکار
- تعداد دفعات پاسخ خودکار
- پرکاربردترین قانون پاسخ
- پرکاربردترین کلیدواژه

### گزارش فیلتر
- تعداد پیام‌های حذف‌شده
- تعداد تخلفات لینک
- تعداد تخلفات کلمات

---

## بازه‌های زمانی
- امروز
- 7 روز اخیر
- بازه سفارشی

---

## منبع داده
- `scheduled_posts`
- `post_logs`
- `auto_reply_logs`
- `moderation_logs`

---

## نمونه کوئری مفهومی

### تعداد پست‌های ارسال‌شده امروز
```sql
SELECT COUNT(*)
FROM scheduled_posts
WHERE status = 'sent'
  AND sent_at::date = CURRENT_DATE;

### تعداد پاسخ‌های خودکار امروز
sql
SELECT COUNT(*)
FROM auto_reply_logs
WHERE created_at::date = CURRENT_DATE;

### تعداد پیام‌های حذف‌شده امروز
sql
SELECT COUNT(*)
FROM moderation_logs
WHERE created_at::date = CURRENT_DATE
  AND result_status = 'success';

---

## نکات مهم
- در MVP گزارش real-time کامل لازم نیست
- گزارش‌ها می‌توانند مستقیم از دیتابیس خوانده شوند
- اگر حجم داده بالا رفت، از summary table استفاده شود


---
