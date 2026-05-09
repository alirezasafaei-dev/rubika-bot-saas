# Auto Replies API

## Endpoints

### Create Rule
`POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies`

Body:

```json
{
  "trigger_text": "hello",
  "reply_text": "hi there",
  "is_active": true
}
```

Response: `AutoReplyResponse`

---

### List Rules
`GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies?page=1&limit=20&is_active=true`

Response:

```json
{
  "items": [],
  "page": 1,
  "limit": 20,
  "total": 0
}
```

---

### Get Rule
`GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}`

---

### Update Rule
`PATCH /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}`

Body (optional fields):

```json
{
  "trigger_text": "hello?",
  "reply_text": "hi!",
  "is_active": false
}
```

---

### Toggle Rule
`POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}/toggle`

Body:

```json
{"is_active": false}
```

---

### Delete Rule
`DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}`

---

### Rule Logs (MVP placeholder)
`GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/logs`

Response:

```json
{
  "items": [],
  "page": 1,
  "limit": 20,
  "total": 0
}
```
