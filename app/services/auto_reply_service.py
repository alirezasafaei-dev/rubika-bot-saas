from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.errors import ErrorCode, NotFoundError
from app.models.auto_reply import AutoReply
from app.repositories.auto_reply_repository import AutoReplyRepository
from app.repositories.channel_repository import ChannelRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class AutoReplyService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.repository = AutoReplyRepository(db_session)
        self.channel_repo = ChannelRepository(db_session)

    async def _ensure_channel_for_workspace(
        self,
        *,
        workspace_id: int,
        channel_id: int,
    ) -> None:
        channel = await self.channel_repo.get_by_id(channel_id)
        if channel is None or channel.workspace_id != workspace_id:
            raise NotFoundError(
                error_code=ErrorCode.CHANNEL_NOT_FOUND,
                message="Channel not found",
            )

    async def create_reply(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        trigger_text: str,
        reply_text: str,
        is_active: bool,
    ) -> AutoReply:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        rule = await self.repository.create(
            channel_id=channel_id,
            trigger_text=trigger_text,
            reply_text=reply_text,
            is_active=is_active,
        )
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def list_replies(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        page: int,
        limit: int,
        is_active: bool | None = None,
    ) -> tuple[list[AutoReply], int]:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        return await self.repository.list_by_channel(
            channel_id=channel_id,
            page=page,
            limit=limit,
            is_active=is_active,
        )

    async def get_reply(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        rule_id: int,
    ) -> AutoReply:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        reply = await self.repository.get_by_id_and_channel(
            rule_id=rule_id,
            channel_id=channel_id,
        )
        if reply is None:
            raise NotFoundError(
                error_code=ErrorCode.AUTO_REPLY_NOT_FOUND,
                message="Auto reply not found",
            )
        return reply

    async def update_reply(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        rule_id: int,
        trigger_text: str | None,
        reply_text: str | None,
        is_active: bool | None,
    ) -> AutoReply:
        reply = await self.get_reply(
            workspace_id=workspace_id,
            channel_id=channel_id,
            rule_id=rule_id,
        )
        updated_reply = await self.repository.update(
            rule=reply,
            trigger_text=trigger_text,
            reply_text=reply_text,
            is_active=is_active,
        )
        await self.db.commit()
        await self.db.refresh(updated_reply)
        return updated_reply

    async def toggle_reply(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        rule_id: int,
        is_active: bool,
    ) -> AutoReply:
        return await self.update_reply(
            workspace_id=workspace_id,
            channel_id=channel_id,
            rule_id=rule_id,
            trigger_text=None,
            reply_text=None,
            is_active=is_active,
        )

    async def delete_reply(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        rule_id: int,
    ) -> None:
        reply = await self.get_reply(
            workspace_id=workspace_id,
            channel_id=channel_id,
            rule_id=rule_id,
        )
        await self.repository.delete(rule=reply)
        await self.db.commit()

    async def get_logs(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        page: int,
        limit: int,
    ) -> tuple[list[dict[str, object]], int]:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        # Logs table not implemented in MVP yet.
        del page, limit
        return [], 0
