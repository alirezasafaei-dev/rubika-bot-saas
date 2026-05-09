from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_channel_service, get_current_user
from app.models.user import User
from app.schemas.channel import ChannelCreate, ChannelResponse, ChannelUpdate
from app.services.channel_service import ChannelService

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post(
    "",
    response_model=ChannelResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_channel(
    workspace_id: int,
    payload: ChannelCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ChannelService, Depends(get_channel_service)],
) -> ChannelResponse:
    del current_user
    channel = await service.create_channel(
        workspace_id=workspace_id,
        payload=payload,
    )
    return ChannelResponse.model_validate(channel)


@router.get("", response_model=list[ChannelResponse])
async def list_channels(
    workspace_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ChannelService, Depends(get_channel_service)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[ChannelResponse]:
    del current_user
    items, _total = await service.list_channels(
        workspace_id=workspace_id,
        page=page,
        limit=limit,
    )
    return [ChannelResponse.model_validate(item) for item in items]


@router.get("/{channel_id}", response_model=ChannelResponse)
async def get_channel(
    workspace_id: int,
    channel_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ChannelService, Depends(get_channel_service)],
) -> ChannelResponse:
    del current_user
    channel = await service.get_channel(
        workspace_id=workspace_id,
        channel_id=channel_id,
    )
    return ChannelResponse.model_validate(channel)


@router.patch("/{channel_id}", response_model=ChannelResponse)
async def update_channel(
    workspace_id: int,
    channel_id: int,
    payload: ChannelUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ChannelService, Depends(get_channel_service)],
) -> ChannelResponse:
    del current_user
    channel = await service.update_channel(
        workspace_id=workspace_id,
        channel_id=channel_id,
        payload=payload,
    )
    return ChannelResponse.model_validate(channel)


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    workspace_id: int,
    channel_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ChannelService, Depends(get_channel_service)],
) -> None:
    del current_user
    await service.delete_channel(
        workspace_id=workspace_id,
        channel_id=channel_id,
    )
