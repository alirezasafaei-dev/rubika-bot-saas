# Webhooks and Events API

## هدف
دریافت eventهای ورودی از روبیکا یا لایه میانی و پردازش آن‌ها در سیستم.

> بسته به مدل اتصال واقعی روبیکا، این بخش ممکن است به webhook مستقیم،
> polling، یا bridge service نیاز داشته باشد.

---

## 1. Incoming Message Webhook

### Endpoint
```http
POST /api/v1/webhooks/rubika/messages

### Headers
http
X-Webhook-Secret: your_webhook_secret

### Request Body
json
{
  "event_type": "message_received",
  "chat": {
"rubika_chat_id": "g0ABCDEF123456",
"type": "group",
"title": "My Group"
  },
  "sender": {
"rubika_user_id": "u0ABCD12345",
"name": "Test User"
  },
  "message": {
"message_id": "m123456",
"text": "قیمت چنده؟",
"sent_at": "2026-05-08T09:10:00Z"
  }
}

### Response
json
{
  "success": true,
  "message": "Webhook received",
  "data": {
"accepted": true
  }
}

---

## 2. Channel Status Event

### Endpoint
http
POST /api/v1/webhooks/rubika/channel-status

### Request Body
json
{
  "event_type": "channel_status_changed",
  "chat": {
"rubika_chat_id": "g0ABCDEF123456"
  },
  "bot_is_admin": true,
  "status": "active"
}

### Response
json
{
  "success": true,
  "message": "Status updated",
  "data": {
"updated": true
  }
}

---

## 3. Delivery Result Callback

اگر برای ارسال پیام، callback یا event نتیجه وجود داشته باشد.

### Endpoint
http
POST /api/v1/webhooks/rubika/delivery-results

### Request Body
json
{
  "event_type": "message_delivery_result",
  "scheduled_post_id": 1,
  "status": "success",
  "provider_message_id": "rm123",
  "response_data": {
"raw": "ok"
  }
}

### Response
json
{
  "success": true,
  "message": "Delivery result processed",
  "data": {
"updated": true
  }
}

---

## نکات امنیتی
- استفاده از secret header
- ثبت IPهای مجاز در صورت امکان
- rate limit
- log کامل درخواست‌های نامعتبر


---
