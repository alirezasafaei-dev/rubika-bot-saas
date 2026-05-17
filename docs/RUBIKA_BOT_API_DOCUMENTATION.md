# Rubika Bot API Documentation

## Introduction

Rubika provides a set of APIs for creating and managing bots.

After creating a bot using `BotFather`, you can interact with the API using HTTP `POST` requests.

---

# Base URL

```http
https://botapi.rubika.ir/v3/{TOKEN}/{METHOD}
```

## Parameters

| Parameter | Description |
|----------|-------------|
| `TOKEN` | Bot token received from BotFather |
| `METHOD` | API method name |

---

# Creating a Bot

## Step 1 — Open BotFather

```text
https://rubika.ir/BotFather
```

Create a new bot and save the generated token.

---

# Receiving Updates

Rubika supports two methods for receiving events from users:

1. Polling (`getUpdates`)
2. Webhook (`Endpoint`)

---

# Method 1 — Polling (`getUpdates`)

In polling mode, your backend periodically requests new updates from Rubika servers.

## Flow

```text
Backend → getUpdates → Rubika
Backend ← Updates ← Rubika
```

---

## Recommended Polling Interval

```text
5 seconds
```

---

## Request Example

```http
POST https://botapi.rubika.ir/v3/{TOKEN}/getUpdates
Content-Type: application/json
```

---

## Offset Handling

Use `start_id` from the previous response to avoid duplicate updates.

---

## Advantages

- Simple implementation
- No HTTPS required
- Suitable for development environments

---

## Disadvantages

- Not real-time
- Delayed message delivery
- Higher unnecessary request volume

---

# Method 2 — Webhook (`Endpoint`)

In webhook mode, Rubika sends events directly to your server using HTTP `POST` requests.

---

# Requirements

## Mandatory

- Public server
- HTTPS enabled
- Valid SSL certificate

---

# Registering Webhook

Use:

```text
updateBotEndpoint
```

to register your server endpoint.

---

# Event Types

---

# Event: `receiveUpdate`

Triggered when:

- User sends a message
- User clicks `ChatKeypad` buttons

---

## HTTP Request

```http
POST /your-webhook-endpoint
Content-Type: application/json
```

---

## Payload Example

```json
{
  "update": {
    "type": "NewMessage",
    "chat_id": "{chat_id}",
    "new_message": {
      "message_id": "{message_id}",
      "text": "custom text",
      "time": "1643122902",
      "is_edited": false,
      "sender_type": "User",
      "sender_id": "{sender_id}",
      "aux_data": {
        "start_id": null,
        "button_id": "{button_id}"
      }
    }
  }
}
```

---

## Object Structure

### `update`

| Field | Type | Description |
|------|------|-------------|
| `type` | string | Event type |
| `chat_id` | string | Chat identifier |
| `new_message` | object | Message data |

---

### `new_message`

| Field | Type | Description |
|------|------|-------------|
| `message_id` | string | Message ID |
| `text` | string | Message text |
| `time` | string | Unix timestamp |
| `is_edited` | boolean | Edited status |
| `sender_type` | string | Sender type |
| `sender_id` | string | Sender ID |
| `aux_data` | object | Extra metadata |

---

### `aux_data`

| Field | Type | Description |
|------|------|-------------|
| `start_id` | string/null | Offset ID |
| `button_id` | string | Button identifier |

---

# Event: `receiveInlineMessage`

Triggered when a user clicks an `InlineKeypad` button.

---

## Payload Example

```json
{
  "inline_message": {
    "sender_id": "{sender_id}",
    "text": "custom text",
    "location": null,
    "aux_data": {
      "start_id": null,
      "button_id": "{button_id}"
    },
    "message_id": "{message_id}",
    "chat_id": "{chat_id}"
  }
}
```

---

## Object Structure

| Field | Type | Description |
|------|------|-------------|
| `sender_id` | string | User ID |
| `text` | string | Callback text |
| `location` | object/null | User location |
| `aux_data` | object | Extra metadata |
| `message_id` | string | Message ID |
| `chat_id` | string | Chat ID |

---

# Recommended Usage

## Development

Use:

```text
getUpdates
```

### Reason

- Easier setup
- No SSL needed
- Better for debugging

---

## Production

Use:

```text
Webhook
```

### Reason

- Real-time events
- Better performance
- Lower latency
- Reduced server load

---

# Suggested Backend Architecture

```text
User Action
    ↓
Rubika Platform
    ↓
Webhook Endpoint
    ↓
Event Handler
    ↓
Business Logic
    ↓
Bot API Response
```

---

# Error Handling

## Recommended HTTP Status Codes

| Status | Meaning |
|--------|---------|
| `200` | Event processed successfully |
| `400` | Invalid payload |
| `401` | Unauthorized |
| `500` | Internal server error |

---

# Security Recommendations

- Use HTTPS only
- Validate incoming requests
- Store bot token securely
- Log webhook requests
- Implement retry handling
- Apply rate limiting

---

# Minimal Webhook Example (Node.js / Express)

```js
const express = require("express");

const app = express();

app.use(express.json());

app.post("/webhook", async (req, res) => {
    const update = req.body;

    console.log(update);

    res.status(200).send("OK");
});

app.listen(3000, () => {
    console.log("Webhook server started");
});
```

---

# Sending Responses

After processing events, use Bot API methods to respond.

Examples:

```text
sendMessage
editMessage
deleteMessage
```

---

# Important Notes

- All API requests must use `POST`
- Webhook works only over HTTPS
- Invalid webhook responses may cause event delivery suspension
- Queue/retry mechanisms are recommended for production systems
