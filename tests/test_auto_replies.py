from __future__ import annotations

import pytest

from app.core.config import settings
from app.models.auto_reply import AutoReply

pytestmark = pytest.mark.asyncio


async def test_create_auto_reply(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {
        "trigger_text": "hello",
        "match_type": "contains",
        "reply_text": "hi",
        "rich_reply": ["more"],
        "is_active": True,
    }

    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["channel_id"] == channel.id
    assert data["trigger_text"] == "hello"
    assert data["reply_text"] == "hi"
    assert data["match_type"] == "contains"
    assert data["rich_reply"] == ["more"]
    assert data["is_active"] is True


async def test_list_auto_replies(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {"trigger_text": "hello", "reply_text": "hi"}

    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json=payload,
        headers=auth_headers,
    )

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies?page=1&limit=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["total"] >= 1
    assert data["active_count"] >= 1


async def test_list_auto_replies_supports_query(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json={"trigger_text": "billing", "reply_text": "invoice help"},
        headers=auth_headers,
    )
    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json={"trigger_text": "support", "reply_text": "agent help"},
        headers=auth_headers,
    )

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies?query=invoice",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["trigger_text"] == "billing"


async def test_get_auto_reply(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {"trigger_text": "hello", "reply_text": "hi"}
    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json=create_payload,
        headers=auth_headers,
    )
    rule_id = create_response.json()["id"]

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies/{rule_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rule_id
    assert data["trigger_text"] == "hello"


async def test_update_auto_reply(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {"trigger_text": "hello", "reply_text": "hi"}
    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json=create_payload,
        headers=auth_headers,
    )
    rule_id = create_response.json()["id"]

    update_payload = {
        "trigger_text": "hello updated",
        "match_type": "exact",
        "reply_text": "hi updated",
        "rich_reply": ["more details"],
        "is_active": False,
    }
    response = await async_client.patch(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies/{rule_id}",
        json=update_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["trigger_text"] == "hello updated"
    assert data["reply_text"] == "hi updated"
    assert data["match_type"] == "exact"
    assert data["rich_reply"] == ["more details"]
    assert data["is_active"] is False


async def test_toggle_auto_reply(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {"trigger_text": "hello", "reply_text": "hi"}
    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json=create_payload,
        headers=auth_headers,
    )
    rule_id = create_response.json()["id"]

    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies/{rule_id}/toggle",
        json={"is_active": False},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["is_active"] is False


async def test_delete_auto_reply(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {"trigger_text": "hello", "reply_text": "hi"}
    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json=create_payload,
        headers=auth_headers,
    )
    rule_id = create_response.json()["id"]

    response = await async_client.delete(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies/{rule_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204


async def test_get_auto_reply_logs(
    async_client,
    auth_headers,
    workspace,
    channel,
    db_session,
):
    rule = AutoReply(channel_id=channel.id, trigger_text="hello", reply_text="hi")
    db_session.add(rule)
    await db_session.commit()
    await db_session.refresh(rule)

    webhook_response = await async_client.post(
        f"/api/v1/webhooks/rubika/{channel.id}",
        json={
            "event_type": "message_received",
            "message": "say hello",
            "sender_rubika_user_id": "u2",
            "message_id": "log-1",
        },
        headers=(
            {"X-Webhook-Secret": settings.webhook_secret}
            if settings.webhook_secret
            else None
        ),
    )
    assert webhook_response.status_code == 200

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies/logs?page=1&limit=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert data["items"][0]["rule_id"] == rule.id


async def test_create_auto_reply_with_next_step(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    next_step = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json={"trigger_text": "step-2", "reply_text": "done"},
        headers=auth_headers,
    )
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json={
            "trigger_text": "step-1",
            "reply_text": "start",
            "next_step_id": next_step.json()["id"],
        },
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["next_step_id"] == next_step.json()["id"]
