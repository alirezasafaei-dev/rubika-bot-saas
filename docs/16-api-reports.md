# Reports API

## 1. Workspace Summary Report

### Endpoint
```http
GET /api/v1/workspaces/{workspace_id}/reports/summary?from=2026-05-01&to=2026-05-07

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"workspace_id": 1,
"from": "2026-05-01",
"to": "2026-05-07",
"summary": {
"created_posts": 12,
"scheduled_posts": 10,
"sent_posts": 9,
"failed_posts": 1,
"auto_replies_sent": 23,
"deleted_messages": 8
}
  }
}

---

## 2. Channel Summary Report

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/reports/summary?from=2026-05-01&to=2026-05-07

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"workspace_id": 1,
"channel_id": 1,
"from": "2026-05-01",
"to": "2026-05-07",
"summary": {
"created_posts": 12,
"scheduled_posts": 10,
"sent_posts": 9,
"failed_posts": 1,
"auto_replies_sent": 23,
"deleted_messages": 8
}
  }
}

---

## 3. Daily Report

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/reports/daily?days=7

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"date": "2026-05-01",
"sent_posts": 2,
"failed_posts": 0,
"auto_replies_sent": 4,
"deleted_messages": 1
},
{
"date": "2026-05-02",
"sent_posts": 1,
"failed_posts": 1,
"auto_replies_sent": 3,
"deleted_messages": 2
}
]
  }
}

---

## قواعد گزارش‌گیری
- `from` و `to` باید معتبر باشند
- اگر `channel_id` داده شد، گزارش محدود به همان کانال باشد
- زمان‌ها بهتر است بر اساس UTC ذخیره و در UI تبدیل شوند


---
