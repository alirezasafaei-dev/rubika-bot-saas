# Scheduled Posts API

## 1. Create Scheduled Post

### Endpoint
```http
POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts

### Request Body
json
{
  "content_type": "text",
  "text_content": "سلام، این یک پست زمان‌بندی‌شده است.",
  "media_url": null,
  "media_file_id": null,
  "caption": null,
  "scheduled_at": "2026-05-08T12:30:00Z",
  "status": "scheduled"
}

### Validation
- `content_type`: `text` or `media`
- اگر `content_type = text`، حداقل یکی از `text_content`
- اگر `content_type = media`، حداقل یکی از `media_url` یا `media_file_id`
- `scheduled_at`: required, must be future datetime

### Response
json
{
  "success": true,
  "message": "Scheduled post created successfully",
  "data": {
"id": 1,
"workspace_id": 1,
"channel_id": 1,
"content_type": "text",
"text_content": "سلام، این یک پست زمان‌بندی‌شده است.",
"scheduled_at": "2026-05-08T12:30:00Z",
"status": "scheduled",
"retry_count": 0,
"created_at": "2026-05-07T10:00:00Z"
  }
}

---

## 2. List Scheduled Posts

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts?page=1&limit=20&status=scheduled

### Query Params
- `page`
- `limit`
- `status`
- `from`
- `to`

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"id": 1,
"content_type": "text",
"text_content": "سلام، این یک پست زمان‌بندی‌شده است.",
"scheduled_at": "2026-05-08T12:30:00Z",
"status": "scheduled",
"sent_at": null,
"error_message": null
}
],
"pagination": {
"page": 1,
"limit": 20,
"total_items": 1,
"total_pages": 1
}
  }
}

---

## 3. Get Scheduled Post Detail

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"id": 1,
"workspace_id": 1,
"channel_id": 1,
"content_type": "text",
"text_content": "سلام، این یک پست زمان‌بندی‌شده است.",
"media_url": null,
"caption": null,
"scheduled_at": "2026-05-08T12:30:00Z",
"status": "scheduled",
"sent_at": null,
"error_message": null,
"retry_count": 0,
"logs": []
  }
}

---

## 4. Update Scheduled Post

### Endpoint
http
PATCH /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}

### Request Body
json
{
  "text_content": "نسخه ویرایش‌شده پست",
  "scheduled_at": "2026-05-08T14:00:00Z",
  "status": "scheduled"
}

### قوانین
- فقط پست‌های `draft`, `scheduled`, `failed` قابل ویرایش هستند
- پست `sent` قابل ویرایش نیست
- پست `sending` فقط در شرایط خاص باید قفل شود

### Response
json
{
  "success": true,
  "message": "Scheduled post updated successfully",
  "data": {
"id": 1,
"text_content": "نسخه ویرایش‌شده پست",
"scheduled_at": "2026-05-08T14:00:00Z",
"status": "scheduled"
  }
}

---

## 5. Cancel Scheduled Post

### Endpoint
http
POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}/cancel

### Response
json
{
  "success": true,
  "message": "Scheduled post cancelled successfully",
  "data": {
"id": 1,
"status": "cancelled"
  }
}

---

## 6. Delete Scheduled Post

### Endpoint
http
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}

### قوانین
- فقط اگر `status != sent` حذف شود
- در عمل بهتر است soft delete پیاده شود

### Response
json
{
  "success": true,
  "message": "Scheduled post deleted successfully",
  "data": null
}

---

## 7. Get Scheduled Post Logs

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}/logs

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"id": 1,
"attempt_no": 1,
"status": "failed",
"error_message": "Temporary API error",
"created_at": "2026-05-08T12:30:03Z"
}
]
  }
}


---
