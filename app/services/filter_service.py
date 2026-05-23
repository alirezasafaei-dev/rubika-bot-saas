from __future__ import annotations

import re
from typing import TYPE_CHECKING

from app.core.errors import AppException, ErrorCode, NotFoundError
from app.models.filter import Filter
from app.repositories.channel_repository import ChannelRepository
from app.repositories.filter_repository import FilterRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.filter import FilterAction, FilterMatchType


class FilterService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.repository = FilterRepository(db_session)
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

    async def create_filter(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        pattern: str,
        match_type: FilterMatchType,
        action: FilterAction,
        reason: str | None,
        is_active: bool,
    ) -> Filter:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        self._validate_pattern(pattern=pattern, match_type=match_type)
        rule = await self.repository.create(
            channel_id=channel_id,
            pattern=pattern,
            match_type=match_type,
            action=action,
            reason=reason,
            is_active=is_active,
        )
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def list_filters(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        page: int,
        limit: int,
        is_active: bool | None = None,
        query: str | None = None,
    ) -> tuple[list[Filter], int, int]:
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

    async def get_filter(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        rule_id: int,
    ) -> Filter:
        await self._ensure_channel_for_workspace(
            workspace_id=workspace_id,
            channel_id=channel_id,
        )
        rule = await self.repository.get_by_id_and_channel(
            filter_id=rule_id,
            channel_id=channel_id,
        )
        if rule is None:
            raise NotFoundError(
                error_code=ErrorCode.FILTER_NOT_FOUND,
                message="Filter not found",
            )
        return rule

    async def update_filter(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        rule_id: int,
        pattern: str | None,
        match_type: FilterMatchType | None,
        action: FilterAction | None,
        reason: str | None,
        is_active: bool | None,
    ) -> Filter:
        rule = await self.get_filter(
            workspace_id=workspace_id,
            channel_id=channel_id,
            rule_id=rule_id,
        )
        self._validate_pattern(
            pattern=pattern or rule.pattern,
            match_type=match_type or rule.match_type,
        )
        updated_rule = await self.repository.update(
            rule=rule,
            pattern=pattern,
            match_type=match_type,
            action=action,
            reason=reason,
            is_active=is_active,
        )
        await self.db.commit()
        await self.db.refresh(updated_rule)
        return updated_rule

    async def delete_filter(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        rule_id: int,
    ) -> None:
        rule = await self.get_filter(
            workspace_id=workspace_id,
            channel_id=channel_id,
            rule_id=rule_id,
        )
        await self.repository.delete(rule=rule)
        await self.db.commit()

    @staticmethod
    def _validate_pattern(*, pattern: str, match_type: FilterMatchType) -> None:
        if match_type.value != "regex":
            return
        try:
            re.compile(pattern)
        except re.error as exc:
            raise AppException(
                ErrorCode.VALIDATION_ERROR,
                f"Invalid regex pattern: {exc}",
                status_code=422,
            ) from exc
