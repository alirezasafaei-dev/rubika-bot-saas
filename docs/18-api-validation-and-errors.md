# API Validation and Errors

## فرمت خطا
```json
{
  "success": false,
  "message": "Validation error",
  "error": {
"code": "VALIDATION_ERROR",
"details": [
{
"field": "scheduled_at",
"message": "scheduled_at must be a future datetime"
}
]
  }
}

---

## کدهای خطای پیشنهادی

### عمومی
- `VALIDATION_ERROR`
- `UNAUTHORIZED`
- `FORBIDDEN`
- `NOT_FOUND`
- `CONFLICT`
- `INTERNAL_ERROR`

### Auth
- `INVALID_CREDENTIALS`
- `PHONE_ALREADY_EXISTS`
- `INVALID_REFRESH_TOKEN`
- `USER_BLOCKED`

### Workspace
- `WORKSPACE_NOT_FOUND`
- `WORKSPACE_ACCESS_DENIED`

### Channel
- `CHANNEL_NOT_FOUND`
- `CHANNEL_ALREADY_EXISTS`
- `BOT_NOT_ADMIN`

### Scheduled Posts
- `POST_NOT_FOUND`
- `POST_ALREADY_SENT`
- `POST_NOT_EDITABLE`
- `INVALID_POST_CONTENT`
- `POST_LIMIT_EXCEEDED`

### Auto Replies
- `AUTO_REPLY_NOT_FOUND`
- `AUTO_REPLY_LIMIT_EXCEEDED`
- `INVALID_MATCH_TYPE`

### Filters
- `FILTER_RULE_NOT_FOUND`
- `INVALID_FILTER_TYPE`

### Reports
- `INVALID_DATE_RANGE`

---

## قواعد Validation

### Workspace
- `name` required, max 150

### Channel
- `rubika_chat_id` required
- `title` required
- `type` in `channel`, `group`

### Scheduled Post
- `content_type` in `text`, `media`
- `scheduled_at` must be future datetime
- text post requires `text_content`
- media post requires `media_url` or `media_file_id`

### Auto Reply
- `title` required
- `match_type` in `exact`, `contains`
- `reply_text` required
- `keywords` array length >= 1

### Filter Rule
- `rule_type` in `link`, `word`
- `pattern` required
- `action_type` must be `delete_message`


---
