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
from app.integrations.rubika_sender import SendResult

pytestmark = pytest.mark.asyncio


@pytest.fixture
def capture_send(monkeypatch):
    sent: list[dict] = []

    async def fake_send_text_message(channel_id, text, **kwargs):
        sent.append({"channel_id": channel_id, "text": text, **kwargs})
        return SendResult(ok=True)

    monkeypatch.setattr(
        "app.services.webhook_service.send_text_message",
        fake_send_text_message,
    )
    return sent


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


@pytest.fixture(autouse=True)
def clear_default_webhook_secret():
    original = settings.webhook_secret
    settings.webhook_secret = ""
    yield
    settings.webhook_secret = original


async def test_webhook_accepts_rubika_update_format(
    async_client,
    channel,
):
    response = await async_client.post(
        "/api/v1/webhooks/rubika",
        json={
            "update": {
                "type": "NewMessage",
                "chat_id": channel.rubika_channel_id,
                "new_message": {
                    "message_id": "rm1",
                    "text": "hello",
                    "sender_id": "u2",
                    "chat_id": channel.rubika_channel_id,
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["reason"] == "message_processed"


async def test_webhook_start_menu_sends_real_keypads(
    async_client,
    channel,
    capture_send,
):
    response = await async_client.post(
        "/api/v1/webhooks/rubika",
        json={
            "update": {
                "type": "NewMessage",
                "chat_id": channel.rubika_channel_id,
                "new_message": {
                    "message_id": "start-1",
                    "text": "/start",
                    "sender_id": "u2",
                    "chat_id": channel.rubika_channel_id,
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["reason"] == "menu_reply"
    assert capture_send[0]["chat_keypad_type"] == "New"
    assert capture_send[0]["chat_keypad"]["rows"]
    assert capture_send[0]["inline_keypad"]["rows"]
    assert "خوش آمدی" in capture_send[0]["text"]


async def test_webhook_chat_button_click_routes_to_status(
    async_client,
    channel,
    db_session,
    capture_send,
):
    db_session.add(
        AutoReply(
            channel_id=channel.id,
            trigger_text="hello",
            reply_text="hi",
        )
    )
    db_session.add(
        Filter(
            channel_id=channel.id,
            pattern="spam",
            action=FilterAction.WARN,
        )
    )
    await db_session.commit()

    response = await async_client.post(
        "/api/v1/webhooks/rubika",
        json={
            "update": {
                "type": "NewMessage",
                "chat_id": channel.rubika_channel_id,
                "new_message": {
                    "message_id": "btn-1",
                    "text": "وضعیت",
                    "sender_id": "u2",
                    "chat_id": channel.rubika_channel_id,
                    "aux_data": {"button_id": "menu_status"},
                },
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["reason"] == "menu_reply"
    assert "پاسخ‌خودکار فعال: 1" in capture_send[0]["text"]
    assert "فیلتر فعال: 1" in capture_send[0]["text"]


async def test_webhook_inline_button_click_routes_to_help(
    async_client,
    channel,
    capture_send,
):
    response = await async_client.post(
        "/api/v1/webhooks/rubika",
        json={
            "inline_message": {
                "sender_id": "u2",
                "text": "راهنما",
                "aux_data": {"button_id": "menu_help"},
                "message_id": "inline-1",
                "chat_id": channel.rubika_channel_id,
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["reason"] == "menu_reply"
    assert "راهنما" in capture_send[0]["text"]


async def test_webhook_contact_button_uses_real_config(
    async_client,
    channel,
    capture_send,
):
    original = settings.rubika_support_contact
    settings.rubika_support_contact = "@support-path"
    try:
        response = await async_client.post(
            "/api/v1/webhooks/rubika",
            json={
                "inline_message": {
                    "sender_id": "u2",
                    "text": "تماس",
                    "aux_data": {"button_id": "menu_contact"},
                    "message_id": "inline-2",
                    "chat_id": channel.rubika_channel_id,
                }
            },
        )
    finally:
        settings.rubika_support_contact = original

    assert response.status_code == 200
    assert response.json()["reason"] == "menu_reply"
    assert "@support-path" in capture_send[0]["text"]


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
