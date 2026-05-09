from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_auto_reply(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {"trigger_text": "hello", "reply_text": "hi", "is_active": True}

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
        "reply_text": "hi updated",
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
):
    create_payload = {"trigger_text": "hello", "reply_text": "hi"}
    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies",
        json=create_payload,
        headers=auth_headers,
    )

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/auto-replies/logs?page=1&limit=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["items"] == []
