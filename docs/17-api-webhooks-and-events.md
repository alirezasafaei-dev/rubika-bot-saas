# Webhooks and Events API (MVP)

## Incoming Rubika Webhook

`POST /api/v1/webhooks/rubika/{channel_id}`

Headers:

- `X-Webhook-Secret` (required only when `WEBHOOK_SECRET` is configured)

Body:

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
