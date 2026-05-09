# app/api/deps.py
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db as get_db_session
from app.models.channel import Channel
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.auto_reply_service import AutoReplyService
from app.services.channel_service import ChannelService
from app.services.filter_service import FilterService
from app.services.workspace_service import WorkspaceService

# OAuth2 scheme for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that provides a transactional async DB session."""
    async for session in get_db_session():
        yield session


# ── Repositories ──────────────────────────────────────────────────────


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    return UserRepository(db)


def get_workspace_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BaseRepository[Workspace]:
    return BaseRepository(Workspace, db)


def get_workspace_member_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BaseRepository[WorkspaceMember]:
    return BaseRepository(WorkspaceMember, db)


def get_channel_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> BaseRepository[Channel]:
    return BaseRepository(Channel, db)


# ── Services ─────────────────────────────────────────────────────────


def get_auth_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthService:
    return AuthService(db=db, user_repo=user_repo)


def get_workspace_service(
    workspace_repo: Annotated[
        BaseRepository[Workspace], Depends(get_workspace_repository)
    ],
    member_repo: Annotated[
        BaseRepository[WorkspaceMember], Depends(get_workspace_member_repository)
    ],
) -> WorkspaceService:
    return WorkspaceService(
        workspace_repository=workspace_repo,
        member_repository=member_repo,
    )


def get_channel_service(
    channel_repo: Annotated[BaseRepository[Channel], Depends(get_channel_repository)],
) -> ChannelService:
    return ChannelService(repository=channel_repo)


def get_auto_reply_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AutoReplyService:
    return AutoReplyService(db_session=db)


def get_filter_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> FilterService:
    return FilterService(db_session=db)


# ── Current User ──────────────────────────────────────────────────────


async def get_current_user(
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        ) from exc

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await auth_service.user_repo.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
