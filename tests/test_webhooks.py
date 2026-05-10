from __future__ import annotations

import pytest
from sqlalchemy import select

from app.core.config import settings
from app.models.auto_reply import AutoReply
from app.models.filter import Filter, FilterAction
from app.models.webhook_processing import (
    MessageProcessingLog,
    ProcessingOutcome,
    WebhookEvent,
)

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

    assert response.status_code == 422


async def test_webhook_filters_then_won_t_auto_reply(
    async_client,
    channel,
    db_session,
):
    db_session.add(
        Filter(
            channel_id=channel.id,
            pattern="spam",
            action=FilterAction.DELETE,
        )
    )
    db_session.add(
        AutoReply(
            channel_id=channel.id,
            trigger_text="spam",
            reply_text="ignored",
        )
    )
    await db_session.commit()

    payload = {
        "event_type": "message_received",
        "message": "this is spam test",
        "sender_rubika_user_id": "u1",
        "message_id": "m1",
    }
    response = await async_client.post(
        f"/api/v1/webhooks/rubika/{channel.id}",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json()["reason"] == "filtered"

    log = (
        await db_session.execute(
            select(MessageProcessingLog).where(
                MessageProcessingLog.channel_id == channel.id
            )
        )
    ).scalar_one()
    assert log.outcome == ProcessingOutcome.FILTER_BLOCKED
    assert log.filter_rule_id is not None


async def test_webhook_auto_reply_and_event_dedup(
    async_client,
    channel,
    db_session,
):
    db_session.add(
        AutoReply(
            channel_id=channel.id,
            trigger_text="hello",
            reply_text="hi",
        )
    )
    await db_session.commit()

    payload = {
        "event_type": "message_received",
        "message": "say hello",
        "sender_rubika_user_id": "u1",
        "message_id": "m2",
    }
    first = await async_client.post(
        f"/api/v1/webhooks/rubika/{channel.id}",
        json=payload,
    )
    second = await async_client.post(
        f"/api/v1/webhooks/rubika/{channel.id}",
        json=payload,
    )
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["reason"] == "duplicate"
    assert len(first.json()) > 0

    events = (
        await db_session.execute(
            WebhookEvent.__table__.select().where(WebhookEvent.message_id == "m2")
        )
    ).all()
    assert len(events) == 1
