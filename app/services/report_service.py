from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import and_, func, select

from app.models.channel import Channel
from app.models.scheduled_post import PostStatus, ScheduledPost
from app.models.webhook_processing import MessageProcessingLog, ProcessingOutcome
from app.models.workspace import WorkspaceMember
from app.repositories.message_processing_log_repository import (
    MessageProcessingLogRepository,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class ReportService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.log_repo = MessageProcessingLogRepository(db_session)

    async def _ensure_workspace_member(
        self, *, user_id: int, workspace_id: int
    ) -> None:
        member_count = (
            await self.db.scalar(
                select(func.count(WorkspaceMember.id)).where(
                    WorkspaceMember.user_id == user_id,
                    WorkspaceMember.workspace_id == workspace_id,
                    WorkspaceMember.deleted_at.is_(None),
                )
            )
            or 0
        )
        if member_count == 0:
            raise PermissionError("Workspace access denied")

    async def _ensure_channel(self, *, workspace_id: int, channel_id: int) -> None:
        channel = await self.db.scalar(
            select(Channel.id).where(
                Channel.id == channel_id,
                Channel.workspace_id == workspace_id,
            )
        )
        if channel is None:
            raise FileNotFoundError("Channel not found")

    @staticmethod
    def _parse_iso(value: str | None) -> datetime | None:
        if value is None:
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("Date must be in ISO format") from exc
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed

    def _normalize_range(
        self,
        from_date: str | None,
        to_date: str | None,
    ) -> tuple[datetime, datetime]:
        start_dt = self._parse_iso(from_date) if from_date else None
        end_dt = self._parse_iso(to_date) if to_date else None

        if start_dt is None and end_dt is None:
            end_dt = datetime.now(tz=UTC)
            start_dt = end_dt - timedelta(days=30)
        elif start_dt is None:
            assert end_dt is not None
            start_dt = end_dt - timedelta(days=30)
        elif end_dt is None:
            end_dt = datetime.now(tz=UTC)

        assert start_dt is not None and end_dt is not None
        if start_dt > end_dt:
            raise ValueError("from_date must be earlier than to_date")
        return start_dt, end_dt

    async def _count_posts(
        self,
        *,
        workspace_id: int,
        channel_id: int | None,
        start_dt: datetime,
        end_dt: datetime,
    ) -> tuple[int, int, int]:
        base_where = [
            Channel.workspace_id == workspace_id,
            Channel.id == ScheduledPost.channel_id,
            ScheduledPost.created_at >= start_dt,
            ScheduledPost.created_at <= end_dt,
        ]
        if channel_id is not None:
            base_where.append(Channel.id == channel_id)

        total_stmt = (
            select(func.count(ScheduledPost.id)).where(*base_where).select_from(Channel)
        )
        total = int((await self.db.execute(total_stmt)).scalar_one())

        sent_stmt = (
            select(func.count(ScheduledPost.id))
            .where(
                *base_where,
                ScheduledPost.status == PostStatus.SENT,
            )
            .select_from(Channel)
        )
        sent = int((await self.db.execute(sent_stmt)).scalar_one())

        failed_stmt = (
            select(func.count(ScheduledPost.id))
            .where(
                *base_where,
                ScheduledPost.status == PostStatus.FAILED,
            )
            .select_from(Channel)
        )
        failed = int((await self.db.execute(failed_stmt)).scalar_one())
        return total, sent, failed

    async def get_workspace_summary(
        self,
        *,
        workspace_id: int,
        user_id: int,
        from_date: str | None,
        to_date: str | None,
    ) -> dict[str, object]:
        await self._ensure_workspace_member(user_id=user_id, workspace_id=workspace_id)
        start_dt, end_dt = self._normalize_range(from_date=from_date, to_date=to_date)
        total, sent, failed = await self._count_posts(
            workspace_id=workspace_id,
            channel_id=None,
            start_dt=start_dt,
            end_dt=end_dt,
        )
        channel_ids = list(
            (
                await self.db.execute(
                    select(Channel.id).where(Channel.workspace_id == workspace_id)
                )
            )
            .scalars()
            .all()
        )
        auto_reply_count = await self.log_repo.count_auto_replies_sent(
            channel_ids=channel_ids,
            since=start_dt,
            until=end_dt,
        )
        filter_count = await self.log_repo.count_filtered_messages(
            channel_ids=channel_ids,
            since=start_dt,
            until=end_dt,
        )
        delivery_result_count = await self.log_repo.count_by_outcome(
            channel_ids=channel_ids,
            outcome=ProcessingOutcome.DELIVERY_RESULT,
            since=start_dt,
            until=end_dt,
        )
        error_count = await self.log_repo.count_by_outcome(
            channel_ids=channel_ids,
            outcome=ProcessingOutcome.ERROR,
            since=start_dt,
            until=end_dt,
        )
        return {
            "created_posts": total,
            "scheduled_posts": total,
            "sent_posts": sent,
            "failed_posts": failed,
            "auto_replies_sent": auto_reply_count,
            "deleted_messages": filter_count,
            "webhook_delivery_results": delivery_result_count,
            "webhook_processing_errors": error_count,
        }

    async def get_channel_summary(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        user_id: int,
        from_date: str | None,
        to_date: str | None,
    ) -> dict[str, object]:
        await self._ensure_workspace_member(user_id=user_id, workspace_id=workspace_id)
        await self._ensure_channel(workspace_id=workspace_id, channel_id=channel_id)
        start_dt, end_dt = self._normalize_range(from_date=from_date, to_date=to_date)
        total, sent, failed = await self._count_posts(
            workspace_id=workspace_id,
            channel_id=channel_id,
            start_dt=start_dt,
            end_dt=end_dt,
        )
        auto_reply_count = await self.log_repo.count_auto_replies_sent(
            channel_ids=[channel_id],
            since=start_dt,
            until=end_dt,
        )
        filter_count = await self.log_repo.count_filtered_messages(
            channel_ids=[channel_id],
            since=start_dt,
            until=end_dt,
        )
        delivery_result_count = await self.log_repo.count_by_outcome(
            channel_ids=[channel_id],
            outcome=ProcessingOutcome.DELIVERY_RESULT,
            since=start_dt,
            until=end_dt,
        )
        error_count = await self.log_repo.count_by_outcome(
            channel_ids=[channel_id],
            outcome=ProcessingOutcome.ERROR,
            since=start_dt,
            until=end_dt,
        )
        return {
            "created_posts": total,
            "scheduled_posts": total,
            "sent_posts": sent,
            "failed_posts": failed,
            "auto_replies_sent": auto_reply_count,
            "deleted_messages": filter_count,
            "webhook_delivery_results": delivery_result_count,
            "webhook_processing_errors": error_count,
        }

    async def get_daily(
        self,
        *,
        workspace_id: int,
        user_id: int,
        days: int,
    ) -> list[dict[str, object]]:
        await self._ensure_workspace_member(user_id=user_id, workspace_id=workspace_id)
        if days <= 0:
            raise ValueError("days must be greater than 0")

        end_dt = datetime.now(tz=UTC).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        start_dt = (end_dt - timedelta(days=days - 1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        posts = (
            await self.db.execute(
                select(ScheduledPost.created_at, ScheduledPost.status)
                .join(Channel, Channel.id == ScheduledPost.channel_id)
                .where(
                    and_(
                        Channel.workspace_id == workspace_id,
                        ScheduledPost.created_at >= start_dt,
                        ScheduledPost.created_at <= end_dt,
                    )
                )
            )
        ).all()

        channel_ids = list(
            (
                await self.db.execute(
                    select(Channel.id).where(Channel.workspace_id == workspace_id)
                )
            )
            .scalars()
            .all()
        )
        logs = list(
            (
                await self.db.execute(
                    select(
                        MessageProcessingLog.created_at,
                        MessageProcessingLog.outcome,
                    ).where(
                        MessageProcessingLog.channel_id.in_(channel_ids),
                        MessageProcessingLog.created_at >= start_dt,
                        MessageProcessingLog.created_at <= end_dt,
                    )
                )
            ).all()
        )

        buckets: dict[str, dict[str, int]] = {}
        for i in range(days):
            key = (start_dt + timedelta(days=i)).date().isoformat()
            buckets[key] = {
                "sent_posts": 0,
                "failed_posts": 0,
                "auto_replies_sent": 0,
                "deleted_messages": 0,
                "webhook_processing_errors": 0,
            }

        for created_at, status in posts:
            key = created_at.date().isoformat()
            if key not in buckets:
                continue
            if status == PostStatus.SENT:
                buckets[key]["sent_posts"] += 1
            if status == PostStatus.FAILED:
                buckets[key]["failed_posts"] += 1

        for created_at, outcome in logs:
            key = created_at.date().isoformat()
            if key not in buckets:
                continue
            if outcome == ProcessingOutcome.AUTO_REPLIED:
                buckets[key]["auto_replies_sent"] += 1
            elif outcome == ProcessingOutcome.FILTER_BLOCKED:
                buckets[key]["deleted_messages"] += 1
            elif outcome == ProcessingOutcome.ERROR:
                buckets[key]["webhook_processing_errors"] += 1

        return [
            {
                "date": key,
                "sent_posts": metrics["sent_posts"],
                "failed_posts": metrics["failed_posts"],
                "auto_replies_sent": metrics["auto_replies_sent"],
                "deleted_messages": metrics["deleted_messages"],
                "webhook_processing_errors": metrics["webhook_processing_errors"],
            }
            for key, metrics in buckets.items()
        ]
