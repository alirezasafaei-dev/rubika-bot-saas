# Auto Reply API

## 1. Create Auto Reply Rule

### Endpoint
```http
POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies

### Request Body
json
{
  "title": "Price Reply",
  "match_type": "contains",
  "reply_text": "برای دریافت تعرفه، لطفاً به پیام پین‌شده مراجعه کنید.",
  "priority": 10,
  "is_active": true,
  "keywords": ["قیمت", "تعرفه", "هزینه"]
}

### Validation
- `title`: required
- `match_type`: `exact` or `contains`
- `reply_text`: required
- `priority`: integer
- `keywords`: array, at least 1 item

### Response
json
{
  "success": true,
  "message": "Auto reply rule created successfully",
  "data": {
"id": 1,
"title": "Price Reply",
"match_type": "contains",
"reply_text": "برای دریافت تعرفه، لطفاً به پیام پین‌شده مراجعه کنید.",
"priority": 10,
"is_active": true,
"keywords": [
"قیمت",
"تعرفه",
"هزینه"
]
  }
}

---

## 2. List Auto Reply Rules

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies?page=1&limit=20&is_active=true

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"id": 1,
"title": "Price Reply",
"match_type": "contains",
"reply_text": "برای دریافت تعرفه، لطفاً به پیام پین‌شده مراجعه کنید.",
"priority": 10,
"is_active": true,
"keywords": ["قیمت", "تعرفه", "هزینه"]
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

## 3. Get Auto Reply Rule Detail

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"id": 1,
"title": "Price Reply",
"match_type": "contains",
"reply_text": "برای دریافت تعرفه، لطفاً به پیام پین‌شده مراجعه کنید.",
"priority": 10,
"is_active": true,
"keywords": ["قیمت", "تعرفه", "هزینه"]
  }
}

---

## 4. Update Auto Reply Rule

### Endpoint
http
PATCH /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}

### Request Body
json
{
  "title": "Updated Price Reply",
  "match_type": "contains",
  "reply_text": "برای دریافت تعرفه جدید، به پست آخر مراجعه کنید.",
  "priority": 5,
  "is_active": true,
  "keywords": ["قیمت", "تعرفه"]
}

### Response
json
{
  "success": true,
  "message": "Auto reply rule updated successfully",
  "data": {
"id": 1,
"title": "Updated Price Reply",
"match_type": "contains",
"reply_text": "برای دریافت تعرفه جدید، به پست آخر مراجعه کنید.",
"priority": 5,
"is_active": true,
"keywords": ["قیمت", "تعرفه"]
  }
}

---

## 5. Toggle Auto Reply Rule

### Endpoint
http
POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}/toggle

### Request Body
json
{
  "is_active": false
}

### Response
json
{
  "success": true,
  "message": "Auto reply rule updated successfully",
  "data": {
"id": 1,
"is_active": false
  }
}

---

## 6. Delete Auto Reply Rule

### Endpoint
http
DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}

### Response
json
{
  "success": true,
  "message": "Auto reply rule deleted successfully",
  "data": null
}

---

## 7. Get Auto Reply Logs

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/logs?page=1&limit=20

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
"incoming_message": "قیمت چنده؟",
"matched_keyword": "قیمت",
"reply_text": "برای دریافت تعرفه، لطفاً به پیام پین‌شده مراجعه کنید.",
"created_at": "2026-05-08T09:10:00Z"
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

