# Webhooks and Events API

## Incoming Rubika Webhook

`POST /api/v1/webhooks/rubika/{channel_id}` or `POST /api/v1/webhooks/rubika`

Headers:

- `X-Webhook-Secret` (required only when `WEBHOOK_SECRET` is configured)

Body (internal format):

```json
{
  "event_type": "message_received",
  "message": "hello",
  "sender_rubika_user_id": "u123",
  "message_id": "m456"
}
```

Accepted event types:

- `message_received`
- `delivery_result`

Response:

```json
{
  "accepted": true,
  "reason": "accepted:message_received"
}
```

Invalid secret => `401`.
Unknown channel => `404`.
Unsupported event type => `400`.
- برای اتصال مستقیم روبیکا (Webhook): مسیر بدون `channel_id`
  - `POST /api/v1/webhooks/rubika`
  - در این حالت `chat_id` از payload استخراج می‌شود و به صورت داخلی به `channel_id` تبدیل می‌گردد.

Body (Rubika webhook format):

```json
{
  "update": {
    "type": "NewMessage",
    "chat_id": "1234567890",
    "new_message": {
      "message_id": "m001",
      "text": "hello",
      "sender_id": "u001"
    }
  }
}
```
