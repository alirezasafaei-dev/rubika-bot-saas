# Reports API

## 1) Workspace Summary Report

### Endpoint
`GET /api/v1/workspaces/{workspace_id}/reports/summary?from=2026-05-01&to=2026-05-07`

### Response
```json
{
  "workspace_id": 1,
  "from_date": "2026-05-01",
  "to_date": "2026-05-07",
  "summary": {
    "created_posts": 12,
    "scheduled_posts": 12,
    "sent_posts": 9,
    "failed_posts": 1,
    "auto_replies_sent": 0,
    "deleted_messages": 0
  }
}
```

- `auto_replies_sent` and `deleted_messages` are MVP placeholders currently derived from configured auto-reply/filter rows.

---

## 2) Channel Summary Report

### Endpoint
`GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/reports/summary?from=2026-05-01&to=2026-05-07`

### Response
```json
{
  "workspace_id": 1,
  "channel_id": 1,
  "from_date": "2026-05-01",
  "to_date": "2026-05-07",
  "summary": {
    "created_posts": 8,
    "scheduled_posts": 8,
    "sent_posts": 6,
    "failed_posts": 2,
    "auto_replies_sent": 0,
    "deleted_messages": 0
  }
}
```

---

## 3) Daily Report

### Endpoint
`GET /api/v1/workspaces/{workspace_id}/reports/daily?days=7`

### Response
```json
{
  "workspace_id": 1,
  "items": [
    {
      "date": "2026-05-01",
      "sent_posts": 2,
      "failed_posts": 0,
      "auto_replies_sent": 0,
      "deleted_messages": 0
    },
    {
      "date": "2026-05-02",
      "sent_posts": 1,
      "failed_posts": 1,
      "auto_replies_sent": 0,
      "deleted_messages": 0
    }
  ]
}
```

---

## گزارش‌گیری قوانین
- `from` و `to` باید فرمت ISO داشته باشند (مثال: `2026-05-01T00:00:00+00:00`)
- اگر بازه زمانی ارسال نشود، پنجره 30 روز گذشته در نظر گرفته می‌شود
- زمانی که دیتای پیام-رویداد (نظیر auto-reply hits و حذف) هنوز ذخیره نشده باشد، این فیلدها صفر می‌مانند
