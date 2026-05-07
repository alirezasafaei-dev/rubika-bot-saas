
# Workspace API

## 1. Create Workspace

### Endpoint
```http
POST /api/v1/workspaces

### Request Body
json
{
  "name": "My Business Workspace"
}

### Response
json
{
  "success": true,
  "message": "Workspace created successfully",
  "data": {
"id": 1,
"name": "My Business Workspace",
"owner_user_id": 1,
"status": "active",
"created_at": "2026-05-07T10:00:00Z"
  }
}

---

## 2. List Workspaces

### Endpoint
http
GET /api/v1/workspaces?page=1&limit=20

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"items": [
{
"id": 1,
"name": "My Business Workspace",
"status": "active",
"created_at": "2026-05-07T10:00:00Z"
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

## 3. Get Workspace Detail

### Endpoint
http
GET /api/v1/workspaces/{workspace_id}

### Response
json
{
  "success": true,
  "message": "OK",
  "data": {
"id": 1,
"name": "My Business Workspace",
"owner_user_id": 1,
"status": "active",
"subscription": {
"plan_name": "free",
"status": "active",
"max_channels": 1,
"max_scheduled_posts": 50,
"max_auto_reply_rules": 10
}
  }
}

---

## 4. Update Workspace

### Endpoint
http
PATCH /api/v1/workspaces/{workspace_id}

### Request Body
json
{
  "name": "Updated Workspace Name",
  "status": "active"
}

### Response
json
{
  "success": true,
  "message": "Workspace updated successfully",
  "data": {
"id": 1,
"name": "Updated Workspace Name",
"status": "active"
  }
}

---

## 5. Delete Workspace

### Endpoint
http
DELETE /api/v1/workspaces/{workspace_id}

### Response
json
{
  "success": true,
  "message": "Workspace deleted successfully",
  "data": null
}

---

## قوانین دسترسی
- فقط owner یا member مجاز به مشاهده Workspace است
- فقط owner مجاز به حذف Workspace است


---
