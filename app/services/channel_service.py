# app/services/channel_service.py
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ErrorCode, NotFoundError, ConflictError, PermissionDeniedError
from app.models.channel import Channel
from app.models.workspace import WorkspaceMember
from app.repositories.base import BaseRepository


class ChannelService:
    def __init__(self, db: AsyncSession, channel_repo: BaseRepository[Channel]):
        self.db = db
        self.channel_repo = channel_repo

    async def _check_membership(self, workspace_id: int, user_id: int, require_admin: bool = False) -> WorkspaceMember:
        """بررسی عضویت کاربر در workspace و بازگرداندن عضو"""
        result = await self.db.execute(
            select(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.deleted_at.is_(None)
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            raise PermissionDeniedError(ErrorCode.NOT_WORKSPACE_MEMBER)
        if require_admin and member.role not in ("owner", "admin"):
            raise PermissionDeniedError(ErrorCode.NOT_WORKSPACE_ADMIN)
        return member

    async def create_channel(
        self,
        workspace_id: int,
        user_id: int,
        rubika_channel_id: str,
        name: str,
        description: Optional[str] = None,
    ) -> Channel:
        await self._check_membership(workspace_id, user_id, require_admin=True)

        # بررسی تکراری نبودن
        existing = await self.channel_repo.list(
            rubika_channel_id=rubika_channel_id,
            workspace_id=workspace_id,
        )
        if existing:
            raise ConflictError(ErrorCode.CHANNEL_ALREADY_EXISTS)

        channel = await self.channel_repo.create(
            workspace_id=workspace_id,
            rubika_channel_id=rubika_channel_id,
            name=name,
            description=description,
            is_active=True,
        )
        return channel

    async def list_channels(
        self,
        workspace_id: int,
        user_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Channel]:
        await self._check_membership(workspace_id, user_id)
        channels = await self.channel_repo.list(
            offset=offset,
            limit=limit,
            workspace_id=workspace_id,
        )
        return list(channels)

    async def get_channel(self, channel_id: int, workspace_id: int, user_id: int) -> Channel:
        await self._check_membership(workspace_id, user_id)
        try:
            channel = await self.channel_repo.get(id=channel_id, workspace_id=workspace_id)
        except NotFoundError:
            raise NotFoundError(ErrorCode.CHANNEL_NOT_FOUND)
        return channel

    async def update_channel(
        self,
        channel_id: int,
        workspace_id: int,
        user_id: int,
        **data,
    ) -> Channel:
        await self._check_membership(workspace_id, user_id, require_admin=True)
        channel = await self.get_channel(channel_id, workspace_id, user_id)
        updated = await self.channel_repo.update(channel, **data)
        return updated

    async def delete_channel(self, channel_id: int, workspace_id: int, user_id: int) -> None:
        await self._check_membership(workspace_id, user_id, require_admin=True)
        channel = await self.get_channel(channel_id, workspace_id, user_id)
        await self.channel_repo.soft_delete(id=channel_id)

    async def get_channels_count(self, workspace_id: int) -> int:
        return await self.channel_repo.count(workspace_id=workspace_id)
