# app/api/v1/endpoints/channels.py
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.channel import Channel
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.channel import (
    ChannelCreate,
    ChannelListResponse,
    ChannelResponse,
    ChannelUpdate,
)
from app.services.channel_service import ChannelService

router = APIRouter(prefix="/workspaces/{workspace_id}/channels", tags=["channels"])


def get_channel_service(db: AsyncSession = Depends(get_db)) -> ChannelService:
    return ChannelService(db, BaseRepository(Channel, db))


@router.get("/", response_model=ChannelListResponse)
async def list_channels(
    workspace_id: int,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> dict[str, Any]:
    channels = await service.list_channels(workspace_id, current_user.id, offset, limit)
    total = await service.get_channels_count(workspace_id)

    return {
        "items": [ChannelResponse.model_validate(channel) for channel in channels],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("/", response_model=ChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    workspace_id: int,
    data: ChannelCreate,
    current_user: User = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> Channel:
    return await service.create_channel(
        workspace_id=workspace_id,
        user_id=current_user.id,
        rubika_channel_id=data.rubika_channel_id,
        name=data.name,
        description=data.description,
    )


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    workspace_id: int,
    channel_id: int,
    current_user: User = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> Channel:
    return await service.get_channel(channel_id, workspace_id, current_user.id)


@router.patch("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    workspace_id: int,
    channel_id: int,
    data: ChannelUpdate,
    current_user: User = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> Channel:
    update_data = data.model_dump(exclude_unset=True)
    return await service.update_channel(
        channel_id=channel_id,
        workspace_id=workspace_id,
        user_id=current_user.id,
        **update_data,
    )


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    workspace_id: int,
    channel_id: int,
    current_user: User = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> None:
    await service.delete_channel(channel_id, workspace_id, current_user.id)
