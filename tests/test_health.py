# tests/test_health.py
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check() -> None:
    """Test health check endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_readiness_check_ok(monkeypatch) -> None:
    async def fake_database_ready() -> bool:
        return True

    monkeypatch.setattr("app.main._database_ready", fake_database_ready)
    monkeypatch.setattr("app.main.redis_ping", lambda: True)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "services": {"database": "ok", "redis": "ok"},
    }


@pytest.mark.asyncio
async def test_readiness_check_degraded(monkeypatch) -> None:
    async def fake_database_ready() -> bool:
        return False

    monkeypatch.setattr("app.main._database_ready", fake_database_ready)
    monkeypatch.setattr("app.main.redis_ping", lambda: False)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "services": {"database": "error", "redis": "error"},
    }


@pytest.mark.asyncio
async def test_root() -> None:
    """Test root endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
