# Filter API

## 1. Create Filter Rule

### Endpoint
```http
POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters

### Request Body
json
{
  "rule_type": "word",
  "pattern": "تبلیغ",
  "action_type": "delete_message",
  "is_active": true
}

### Validation
- `rule_type`: `link` or `word`
- `pattern`: required
- `action_type`: currently only `delete_message`

### Response
json
{
  "success": true,
  "message": "Filter rule created successfully",
  "data": {
"id": 1,
"rule_type": "word",
"pattern": "تبلیغ",
"action_type": "delete_message",
"is_active": true
  }
}

---

## 2. List Filter Rules

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters?page=1&limit=20

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"id": 1,
"rule_type": "word",
"pattern": "تبلیغ",
"action_type": "delete_message",
"is_active": true
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

## 3. Get Filter Rule Detail

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"id": 1,
"rule_type": "word",
"pattern": "تبلیغ",
"action_type": "delete_message",
"is_active": true
  }
}

---

## 4. Update Filter Rule

### Endpoint
http
PATCH /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}

### Request Body
json
{
  "pattern": "اسپم",
  "is_active": true
}

### Response
json
{
  "success": true,
  "message": "Filter rule updated successfully",
  "data": {
"id": 1,
"rule_type": "word",
"pattern": "اسپم",
"action_type": "delete_message",
"is_active": true
  }
}

---

## 5. Toggle Filter Rule

### Endpoint
http
POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}/toggle

### Request Body
json
{
  "is_active": false
}

### Response
json
{
  "success": true,
  "message": "Filter rule updated successfully",
  "data": {
"id": 1,
"is_active": false
  }
}

---

## 6. Delete Filter Rule

### Endpoint
http
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}

### Response
json
{
  "success": true,
  "message": "Filter rule deleted successfully",
  "data": null
}

---

## 7. Get Moderation Logs

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/logs?page=1&limit=20

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"id": 1,
"rule_id": 1,
"sender_rubika_user_id": "u0ABCD12345",
"message_text": "لینک تبلیغاتی",
"detected_value": "تبلیغ",
"action_type": "delete_message",
"result_status": "success",
"error_message": null,
"created_at": "2026-05-08T11:00:00Z"
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
