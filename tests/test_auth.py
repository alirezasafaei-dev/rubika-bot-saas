# tests/test_auth.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "StrongPassword123",
            "full_name": "Test User",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "StrongPassword123",
            "full_name": "Login User",
        },
    )

    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "StrongPassword123",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_me(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "StrongPassword123",
            "full_name": "Me User",
        },
    )

    login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "me@example.com",
            "password": "StrongPassword123",
        },
    )

    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
