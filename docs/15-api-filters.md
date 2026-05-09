# Filter API (MVP)

## Endpoints

### Create Filter
`POST /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters`

Body:

```json
{
  "pattern": "spam",
  "action": "delete",
  "reason": "spam message",
  "is_active": true
}
```

Supported actions: `delete`, `warn`, `ban`.

---

### List Filters
`GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters?page=1&limit=20&is_active=true`

```json
{
  "items": [],
  "page": 1,
  "limit": 20,
  "total": 0
}
```

---

### Get Filter
`GET /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}`

---

### Update Filter
`PATCH /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}`

```json
{
  "pattern": "ads",
  "is_active": false
}
```

---

### Delete Filter
`DELETE /api/v1/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}`

---

### Notes
- Logs/matching pipeline is out of scope for this phase and will be completed in webhook/message processing phase.
