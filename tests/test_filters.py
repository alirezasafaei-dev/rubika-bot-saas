from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_create_filter(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    payload = {
        "pattern": "spam",
        "match_type": "contains",
        "action": "delete",
        "reason": "spam message",
    }

    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["channel_id"] == channel.id
    assert data["pattern"] == "spam"
    assert data["match_type"] == "contains"
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
    assert data["active_count"] >= 1


async def test_list_filters_supports_query(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json={"pattern": "spam", "action": "delete", "reason": "ads block"},
        headers=auth_headers,
    )
    await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json={"pattern": "scam", "action": "warn", "reason": "fraud"},
        headers=auth_headers,
    )

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters?query=fraud",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["pattern"] == "scam"


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


async def test_create_regex_filter(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json={"pattern": "spam\\d+", "match_type": "regex", "action": "flag"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    assert response.json()["match_type"] == "regex"
    assert response.json()["action"] == "flag"


async def test_reject_invalid_regex_filter(
    async_client,
    auth_headers,
    workspace,
    channel,
):
    response = await async_client.post(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/filters",
        json={"pattern": "(spam", "match_type": "regex", "action": "delete"},
        headers=auth_headers,
    )

    assert response.status_code == 422
