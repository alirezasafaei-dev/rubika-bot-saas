from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.scheduled_post import (
    ScheduledPostCreate,
    ScheduledPostListResponse,
    ScheduledPostLogsResponse,
    ScheduledPostResponse,
    ScheduledPostUpdate,
)
from app.services.scheduled_post_service import ScheduledPostService

router = APIRouter(tags=["scheduled-posts"])

DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post(
    "/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts",
    response_model=ScheduledPostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_scheduled_post(
    workspace_id: int,
    channel_id: int,
    payload: ScheduledPostCreate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> ScheduledPostResponse:
    service = ScheduledPostService(db)
    post = await service.create_post(
        workspace_id=workspace_id,
        channel_id=channel_id,
        payload=payload,
        current_user=current_user,
    )
    return ScheduledPostResponse.model_validate(post)


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts",
    response_model=ScheduledPostListResponse,
)
async def list_scheduled_posts(
    workspace_id: int,
    channel_id: int,
    db: DbSessionDep,
    current_user: CurrentUserDep,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> ScheduledPostListResponse:
    service = ScheduledPostService(db)
    return await service.list_posts(
        workspace_id=workspace_id,
        channel_id=channel_id,
        page=page,
        limit=limit,
        current_user=current_user,
    )


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}",
    response_model=ScheduledPostResponse,
)
async def get_scheduled_post(
    workspace_id: int,
    channel_id: int,
    post_id: int,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> ScheduledPostResponse:
    service = ScheduledPostService(db)
    post = await service.get_post(
        workspace_id=workspace_id,
        channel_id=channel_id,
        post_id=post_id,
        current_user=current_user,
    )
    return ScheduledPostResponse.model_validate(post)


@router.patch(
    "/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}",
    response_model=ScheduledPostResponse,
)
async def update_scheduled_post(
    workspace_id: int,
    channel_id: int,
    post_id: int,
    payload: ScheduledPostUpdate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> ScheduledPostResponse:
    service = ScheduledPostService(db)
    post = await service.update_post(
        workspace_id=workspace_id,
        channel_id=channel_id,
        post_id=post_id,
        payload=payload,
        current_user=current_user,
    )
    return ScheduledPostResponse.model_validate(post)


@router.post(
    "/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}/cancel",
    response_model=ScheduledPostResponse,
)
async def cancel_scheduled_post(
    workspace_id: int,
    channel_id: int,
    post_id: int,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> ScheduledPostResponse:
    service = ScheduledPostService(db)
    post = await service.cancel_post(
        workspace_id=workspace_id,
        channel_id=channel_id,
        post_id=post_id,
        current_user=current_user,
    )
    return ScheduledPostResponse.model_validate(post)


@router.delete(
    "/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_scheduled_post(
    workspace_id: int,
    channel_id: int,
    post_id: int,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> Response:
    service = ScheduledPostService(db)
    await service.delete_post(
        workspace_id=workspace_id,
        channel_id=channel_id,
        post_id=post_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/scheduled-posts/{post_id}/logs",
    response_model=ScheduledPostLogsResponse,
)
async def get_scheduled_post_logs(
    workspace_id: int,
    channel_id: int,
    post_id: int,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> ScheduledPostLogsResponse:
    service = ScheduledPostService(db)
    return await service.get_logs(
        workspace_id=workspace_id,
        channel_id=channel_id,
        post_id=post_id,
        current_user=current_user,
    )
