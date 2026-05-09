from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_scheduled_post(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {
        "content": "scheduled message",
        "scheduled_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }

    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["channel_id"] == channel.id
    assert data["content"] == "scheduled message"
    assert data["status"] == "pending"


async def test_list_scheduled_posts(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {
        "content": "first post",
        "scheduled_at": (datetime.now(UTC) + timedelta(hours=2)).isoformat(),
    }

    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts",
        json=payload,
        headers=auth_headers,
    )

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts?page=1&limit=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["total"] >= 1


async def test_update_pending_scheduled_post(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {
        "content": "old text",
        "scheduled_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }

    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts",
        json=create_payload,
        headers=auth_headers,
    )
    post_id = create_response.json()["id"]

    update_payload = {
        "content": "new text",
        "scheduled_at": (datetime.now(UTC) + timedelta(hours=3)).isoformat(),
    }

    response = await async_client.patch(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts/{post_id}",
        json=update_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "new text"


async def test_cancel_scheduled_post(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {
        "content": "cancel me",
        "scheduled_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }

    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts",
        json=create_payload,
        headers=auth_headers,
    )
    post_id = create_response.json()["id"]

    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts/{post_id}/cancel",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


async def test_delete_scheduled_post(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {
        "content": "delete me",
        "scheduled_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }

    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts",
        json=create_payload,
        headers=auth_headers,
    )
    post_id = create_response.json()["id"]

    response = await async_client.delete(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts/{post_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204


async def test_get_scheduled_post_logs(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {
        "content": "log me",
        "scheduled_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
    }

    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts",
        json=create_payload,
        headers=auth_headers,
    )
    post_id = create_response.json()["id"]

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/scheduled-posts/{post_id}/logs",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
