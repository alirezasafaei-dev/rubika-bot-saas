from __future__ import annotations

import pytest

from app.core.config import settings

pytestmark = pytest.mark.asyncio


async def test_webhook_accepts_valid_channel(
    async_client,
    workspace,
    channel,
):
    payload = {
        "event_type": "message_received",
        "message": "hello",
        "sender_rubika_user_id": "u123",
    }

    response = await async_client.post(
        f"/api/v1/webhooks/rubika/{channel.id}",
        json=payload,
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True


async def test_webhook_rejects_invalid_channel(async_client):
    payload = {"event_type": "message_received"}

    response = await async_client.post("/api/v1/webhooks/rubika/99999", json=payload)

    assert response.status_code == 404


async def test_webhook_secret_validation(
    async_client,
    channel,
):
    original = settings.webhook_secret
    settings.webhook_secret = "super-secret"
    try:
        payload = {"event_type": "message_received"}

        denied = await async_client.post(
            f"/api/v1/webhooks/rubika/{channel.id}",
            json=payload,
        )
        assert denied.status_code == 401

        accepted = await async_client.post(
            f"/api/v1/webhooks/rubika/{channel.id}",
            json=payload,
            headers={"X-Webhook-Secret": "super-secret"},
        )
        assert accepted.status_code == 200
    finally:
        settings.webhook_secret = original


async def test_webhook_rejects_unknown_event_type(
    async_client,
    channel,
):
    payload = {"event_type": "unknown_event"}

    response = await async_client.post(
        f"/api/v1/webhooks/rubika/{channel.id}",
        json=payload,
    )

    assert response.status_code == 400
