from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_filter(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {"pattern": "spam", "action": "delete", "reason": "spam message"}

    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["channel_id"] == channel.id
    assert data["pattern"] == "spam"
    assert data["action"] == "delete"


async def test_list_filters(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {"pattern": "spam", "action": "delete"}

    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json=payload,
        headers=auth_headers,
    )

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters?page=1&limit=20",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["page"] == 1
    assert data["limit"] == 20
    assert data["total"] >= 1


async def test_get_filter(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {"pattern": "spam", "action": "delete"}
    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json=create_payload,
        headers=auth_headers,
    )
    rule_id = create_response.json()["id"]

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters/{rule_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rule_id
    assert data["pattern"] == "spam"


async def test_update_filter(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {"pattern": "spam", "action": "delete"}
    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json=create_payload,
        headers=auth_headers,
    )
    rule_id = create_response.json()["id"]

    response = await async_client.patch(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters/{rule_id}",
        json={"pattern": "ads", "is_active": False},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["pattern"] == "ads"
    assert data["is_active"] is False


async def test_delete_filter(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    create_payload = {"pattern": "spam", "action": "delete"}
    create_response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json=create_payload,
        headers=auth_headers,
    )
    rule_id = create_response.json()["id"]

    response = await async_client.delete(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters/{rule_id}",
        headers=auth_headers,
    )

    assert response.status_code == 204
