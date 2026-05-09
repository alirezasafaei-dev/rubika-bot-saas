from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.security import hash_password
from app.db.base_class import Base
from app.main import app
from app.models.channel import Channel
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.auth import LoginRequest

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "",
)
if not TEST_DATABASE_URL.startswith("sqlite+aiosqlite://"):
    TEST_DATABASE_URL = "sqlite+aiosqlite:///./rubika_test.db"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop() -> AsyncGenerator[asyncio.AbstractEventLoop, None]:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def client(async_client: AsyncClient) -> AsyncClient:
    return async_client


@pytest.fixture(scope="function")
async def auth_headers(async_client: AsyncClient, test_user: User) -> dict[str, str]:
    login_data = LoginRequest(phone=test_user.phone, password="testpassword")
    response = await async_client.post(
        "/api/v1/auth/login", json=login_data.model_dump()
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        full_name="Test User",
        username="testuser",
        phone="+989123456789",
        hashed_password=hash_password("testpassword"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def test_workspace(db_session: AsyncSession, test_user: User) -> Workspace:
    workspace = Workspace(
        owner_id=test_user.id,
        name="Test Workspace",
        description="A test workspace",
    )
    db_session.add(workspace)
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


@pytest.fixture(scope="function")
async def workspace(test_workspace: Workspace) -> Workspace:
    return test_workspace


@pytest.fixture(scope="function")
async def test_channel(
    db_session: AsyncSession,
    test_workspace: Workspace,
) -> Channel:
    channel = Channel(
        workspace_id=test_workspace.id,
        rubika_channel_id="c12345",
        name="Test Channel",
        description="A test channel",
    )
    db_session.add(channel)
    await db_session.commit()
    await db_session.refresh(channel)
    return channel


@pytest.fixture(scope="function")
async def channel(test_channel: Channel) -> Channel:
    return test_channel
