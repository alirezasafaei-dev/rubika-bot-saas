from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio


async def test_validation_error_uses_standard_contract(async_client) -> None:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"phone": "bad", "password": "123"},
    )

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Validation error"
    assert body["error"]["details"]


async def test_authentication_error_uses_standard_contract(async_client) -> None:
    response = await async_client.get("/api/v1/workspaces")
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["message"]


async def test_not_found_error_uses_standard_contract(
    async_client,
    auth_headers,
    workspace,
    workspace_member,
) -> None:
    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/99999/reports/summary",
        headers=auth_headers,
    )
    assert response.status_code == 404
    body = response.json()
    assert body["error"]["code"] == "NOT_FOUND"
