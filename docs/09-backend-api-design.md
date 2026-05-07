# Backend API Design

## هدف
طراحی API بک‌اند برای MVP ربات مدیریتی روبیکا با پوشش کامل نیازهای:
- احراز هویت
- مدیریت Workspace
- مدیریت کانال/گروه
- زمان‌بندی پست
- پاسخ خودکار
- فیلتر محتوا
- گزارش‌گیری
- پردازش webhook/event

---

## اصول کلی API

### Base URL
```text
/api/v1

### Content-Type
http
Content-Type: application/json

### فرمت پاسخ موفق
json
{
  "success": true,
  "message": "OK",
  "data": {}
}

### فرمت پاسخ خطا
json
{
  "success": false,
  "message": "Validation error",
  "error": {
"code": "VALIDATION_ERROR",
"details": [
{
"field": "name",
"message": "name is required"
}
]
  }
}

---

## احراز هویت
برای MVP پیشنهاد می‌شود از JWT استفاده شود.

### هدر احراز هویت
http
Authorization: Bearer <access_token>

---

## ساختار Pagination
### Query Params
- `page`
- `limit`

### نمونه پاسخ
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [],
"pagination": {
"page": 1,
"limit": 20,
"total_items": 100,
"total_pages": 5
}
  }
}

---

## ماژول‌های API
1. Auth
2. Users
3. Workspaces
4. Channels
5. Scheduled Posts
6. Auto Replies
7. Filters
8. Reports
9. Webhooks / Events

---

## کدهای وضعیت HTTP
- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
- `409 Conflict`
- `422 Unprocessable Entity`
- `500 Internal Server Error`

---

## قواعد مهم
- هر منبع باید متعلق به یک Workspace باشد
- دسترسی به منابع فقط برای اعضای Workspace مجاز است
- فیلتر قبل از پاسخ خودکار اجرا می‌شود
- فقط اولین قانون Auto Reply اجرا می‌شود
- پست با وضعیت `sent` دیگر قابل ویرایش نیست


---
