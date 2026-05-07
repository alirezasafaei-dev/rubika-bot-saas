# app/api/v1/endpoints/channels.py
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.errors import AppException
from app.db.dependencies import get_db
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.channel import (
    ChannelCreate,
    ChannelListResponse,
    ChannelResponse,
    ChannelUpdate,
)
from app.services.channel_service import ChannelService
from app.models.channel import Channel

router = APIRouter(prefix="/workspaces/{workspace_id}/channels", tags=["channels"])


def get_channel_service(db: AsyncSession = Depends(get_db)) -> ChannelService:
    return ChannelService(db, BaseRepository(Channel, db))


@router.get("/", response_model=ChannelListResponse)
async def list_channels(
    workspace_id: int,
    offset: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> dict[str, Any]:
    channels = await service.list_channels(workspace_id, current_user.id, offset, limit)
    total = await service.get_channels_count(workspace_id)
    return {
        "items": [ChannelResponse.model_validate(c) for c in channels],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post("/", response_model=ChannelResponse, status_code=201)
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
    return await service.update_channel(channel_id, workspace_id, current_user.id, **update_data)


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(
    workspace_id: int,
    channel_id: int,
    current_user: User = Depends(get_current_user),
    service: ChannelService = Depends(get_channel_service),
) -> None:
    await service.delete_channel(channel_id, workspace_id, current_user.id)
