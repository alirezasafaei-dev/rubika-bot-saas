from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_processing import MessageProcessingLog, ProcessingOutcome


class MessageProcessingLogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        event_id: int | None,
        channel_id: int,
        outcome: ProcessingOutcome,
        filter_rule_id: int | None = None,
        auto_reply_rule_id: int | None = None,
        message_excerpt: str | None = None,
        reason: str | None = None,
    ) -> MessageProcessingLog:
        log = MessageProcessingLog(
            event_id=event_id,
            channel_id=channel_id,
            outcome=outcome,
            filter_rule_id=filter_rule_id,
            auto_reply_rule_id=auto_reply_rule_id,
            message_excerpt=message_excerpt,
            reason=reason,
        )
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log

    async def count_auto_replies_sent(
        self, *, channel_ids: list[int], since: datetime, until: datetime
    ) -> int:
        stmt = select(func.count(MessageProcessingLog.id)).where(
            MessageProcessingLog.channel_id.in_(channel_ids),
            MessageProcessingLog.outcome == ProcessingOutcome.AUTO_REPLIED,
            MessageProcessingLog.created_at >= since,
            MessageProcessingLog.created_at <= until,
        )
        return int((await self.db.scalar(stmt)) or 0)

    async def count_filtered_messages(
        self, *, channel_ids: list[int], since: datetime, until: datetime
    ) -> int:
        stmt = select(func.count(MessageProcessingLog.id)).where(
            MessageProcessingLog.channel_id.in_(channel_ids),
            MessageProcessingLog.outcome == ProcessingOutcome.FILTER_BLOCKED,
            MessageProcessingLog.created_at >= since,
            MessageProcessingLog.created_at <= until,
        )
        return int((await self.db.scalar(stmt)) or 0)

    async def count_by_outcome(
        self,
        *,
        channel_ids: list[int],
        outcome: ProcessingOutcome,
        since: datetime,
        until: datetime,
    ) -> int:
        stmt = select(func.count(MessageProcessingLog.id)).where(
            MessageProcessingLog.channel_id.in_(channel_ids),
            MessageProcessingLog.outcome == outcome,
            MessageProcessingLog.created_at >= since,
            MessageProcessingLog.created_at <= until,
        )
        return int((await self.db.scalar(stmt)) or 0)

    async def list_auto_reply_logs(
        self,
        *,
        channel_id: int,
        page: int,
        limit: int,
    ) -> tuple[list[MessageProcessingLog], int]:
        conditions = [
            MessageProcessingLog.channel_id == channel_id,
            MessageProcessingLog.auto_reply_rule_id.is_not(None),
        ]
        total_stmt = select(func.count(MessageProcessingLog.id)).where(*conditions)
        total = int((await self.db.scalar(total_stmt)) or 0)
        stmt = (
            select(MessageProcessingLog)
            .where(*conditions)
            .order_by(MessageProcessingLog.created_at.desc(), MessageProcessingLog.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total
