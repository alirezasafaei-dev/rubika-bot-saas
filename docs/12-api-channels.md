# Channel API

## 1. Create Channel

### Endpoint
```http
POST /api/v1/workspaces/{workspace_id}/channels

### Request Body
json
{
  "rubika_chat_id": "g0ABCDEF123456",
  "title": "My Group",
  "type": "group",
  "bot_is_admin": true,
  "settings_json": {
"language": "fa"
  }
}

### Validation
- `rubika_chat_id`: required
- `title`: required
- `type`: one of `channel`, `group`

### Response
json
{
  "success": true,
  "message": "Channel created successfully",
  "data": {
"id": 1,
"workspace_id": 1,
"rubika_chat_id": "g0ABCDEF123456",
"title": "My Group",
"type": "group",
"status": "active",
"bot_is_admin": true,
"settings_json": {
"language": "fa"
}
  }
}

---

## 2. List Channels

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels?page=1&limit=20

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"id": 1,
"title": "My Group",
"type": "group",
"status": "active",
"bot_is_admin": true
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

## 3. Get Channel Detail

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"id": 1,
"workspace_id": 1,
"rubika_chat_id": "g0ABCDEF123456",
"title": "My Group",
"type": "group",
"status": "active",
"bot_is_admin": true,
"settings_json": {
"language": "fa"
}
  }
}

---

## 4. Update Channel

### Endpoint
http
PATCH /api/v1/workspaces/{workspace_id}/channels/{channel_id}

### Request Body
json
{
  "title": "Updated Group Title",
  "status": "active",
  "bot_is_admin": true,
  "settings_json": {
"language": "fa",
"timezone": "Asia/Tehran"
  }
}

### Response
json
{
  "success": true,
  "message": "Channel updated successfully",
  "data": {
"id": 1,
"title": "Updated Group Title",
"status": "active",
"bot_is_admin": true
  }
}

---

## 5. Delete Channel

### Endpoint
http
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}

### Response
json
{
  "success": true,
  "message": "Channel deleted successfully",
  "data": null
}

---

## نکات
- حذف Channel باید فقط اگر متعلق به همان Workspace باشد انجام شود
- بهتر است در پیاده‌سازی واقعی از soft delete استفاده شود


---
