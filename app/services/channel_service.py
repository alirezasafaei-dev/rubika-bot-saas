# app/services/channel_service.py
from __future__ import annotations

from app.core.errors import AppException, ErrorCode
from app.models.channel import Channel
from app.repositories.base import BaseRepository
from app.schemas.channel import ChannelCreate, ChannelUpdate


class ChannelService:
    def __init__(self, repository: BaseRepository[Channel]) -> None:
        self.repository = repository

    async def create_channel(
        self,
        *,
        workspace_id: int,
        payload: ChannelCreate,
    ) -> Channel:
        existing = await self.repository.get_one_by(
            workspace_id=workspace_id,
            rubika_channel_id=payload.rubika_channel_id,
        )
        if existing is not None:
            raise AppException(
                ErrorCode.CONFLICT, "Channel already exists in workspace"
            )

        return await self.repository.create(
            workspace_id=workspace_id,
            rubika_channel_id=payload.rubika_channel_id,
            name=payload.name,
            description=payload.description,
        )

    async def list_channels(
        self,
        *,
        workspace_id: int,
        page: int,
        limit: int,
    ) -> tuple[list[Channel], int]:
        items = await self.repository.list(
            workspace_id=workspace_id,
            page=page,
            limit=limit,
            order_by=Channel.id.desc(),
        )
        total = await self.repository.count(workspace_id=workspace_id)
        return list(items), total

    async def get_channel(
        self,
        *,
        workspace_id: int,
        channel_id: int,
    ) -> Channel:
        channel = await self.repository.get_one_by(
            id=channel_id, workspace_id=workspace_id
        )
        if channel is None:
            raise AppException(ErrorCode.NOT_FOUND, "Channel not found")
        return channel

    async def update_channel(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        payload: ChannelUpdate,
    ) -> Channel:
        channel = await self.get_channel(
            workspace_id=workspace_id, channel_id=channel_id
        )

        data = payload.model_dump(exclude_unset=True)
        return await self.repository.update(channel, **data)

    async def delete_channel(
        self,
        *,
        workspace_id: int,
        channel_id: int,
    ) -> None:
        channel = await self.get_channel(
            workspace_id=workspace_id, channel_id=channel_id
        )
        await self.repository.soft_delete(channel)
