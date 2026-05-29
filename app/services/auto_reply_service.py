from __future__ import annotations

import json
from typing import TYPE_CHECKING

from app.core.errors import AppException, ErrorCode, NotFoundError
from app.models.auto_reply import AutoReply
from app.repositories.auto_reply_repository import AutoReplyRepository
from app.repositories.channel_repository import ChannelRepository
from app.repositories.message_processing_log_repository import (
    MessageProcessingLogRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.auto_reply import AutoReplyMatchType


class AutoReplyService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.repository = AutoReplyRepository(db_session)
        self.channel_repo = ChannelRepository(db_session)
        self.log_repo = MessageProcessingLogRepository(db_session)

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
        match_type: AutoReplyMatchType,
        reply_text: str,
        rich_reply: list[str] | None,
        next_step_id: int | None,
        is_active: bool,
    ) -> AutoReply:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        await self._validate_next_step(
            workspace_id=workspace_id,
            channel_id=channel_id,
            next_step_id=next_step_id,
        )
        rule = await self.repository.create(
            channel_id=channel_id,
            trigger_text=trigger_text,
            match_type=match_type,
            reply_text=reply_text,
            rich_reply_json=self._serialize_rich_reply(rich_reply),
            next_step_id=next_step_id,
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
        query: str | None = None,
    ) -> tuple[list[AutoReply], int, int]:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        items, total = await self.repository.list_by_channel(
            channel_id=channel_id,
            page=page,
            limit=limit,
            is_active=is_active,
            query=query,
        )
        active_count = await self.repository.count_active_by_channel(channel_id=channel_id)
        return items, total, active_count

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
        match_type: AutoReplyMatchType | None,
        reply_text: str | None,
        rich_reply: list[str] | None,
        is_active: bool | None,
        next_step_id: int | None,
    ) -> AutoReply:
        reply = await self.get_reply(
            workspace_id=workspace_id,
            channel_id=channel_id,
            rule_id=rule_id,
        )
        if next_step_id == reply.id:
            raise AppException(
                ErrorCode.VALIDATION_ERROR,
                "Auto reply cannot chain to itself",
                status_code=422,
            )
        await self._validate_next_step(
            workspace_id=workspace_id,
            channel_id=channel_id,
            next_step_id=next_step_id,
        )
        updated_reply = await self.repository.update(
            rule=reply,
            trigger_text=trigger_text,
            match_type=match_type,
            reply_text=reply_text,
            rich_reply_json=self._serialize_rich_reply(rich_reply),
            next_step_id=next_step_id,
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
            match_type=None,
            reply_text=None,
            rich_reply=None,
            is_active=is_active,
            next_step_id=None,
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
        logs, total = await self.log_repo.list_auto_reply_logs(
            channel_id=channel_id,
            page=page,
            limit=limit,
        )
        items = [
            {
                "rule_id": log.auto_reply_rule_id,
                "event": log.reason or log.outcome.value,
                "created_at": log.created_at,
            }
            for log in logs
            if log.auto_reply_rule_id is not None
        ]
        return items, total

    async def _validate_next_step(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        next_step_id: int | None,
    ) -> None:
        if next_step_id is None:
            return
        await self.get_reply(
            workspace_id=workspace_id,
            channel_id=channel_id,
            rule_id=next_step_id,
        )

    @staticmethod
    def _serialize_rich_reply(rich_reply: list[str] | None) -> str | None:
        if rich_reply is None:
            return None
        items = [item.strip() for item in rich_reply if item and item.strip()]
        if not items:
            return None
        return json.dumps(items, ensure_ascii=False)
