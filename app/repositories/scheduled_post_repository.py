from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scheduled_post import PostStatus, ScheduledPost


class ScheduledPostRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        channel_id: int,
        content: str,
        scheduled_at: datetime,
    ) -> ScheduledPost:
        obj = ScheduledPost(
            channel_id=channel_id,
            content=content,
            scheduled_at=scheduled_at,
            status=PostStatus.PENDING,
        )
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def list_by_channel(
        self,
        *,
        channel_id: int,
        page: int,
        limit: int,
    ) -> tuple[list[ScheduledPost], int]:
        count_stmt = select(func.count(ScheduledPost.id)).where(
            ScheduledPost.channel_id == channel_id,
        )
        total = int((await self.db.execute(count_stmt)).scalar_one())

        stmt = (
            select(ScheduledPost)
            .where(ScheduledPost.channel_id == channel_id)
            .order_by(ScheduledPost.scheduled_at.asc(), ScheduledPost.id.asc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    async def claim_due_posts(
        self,
        *,
        now: datetime,
        limit: int = 100,
    ) -> Sequence[ScheduledPost]:
        """Claim due posts and move them to queued state atomically.

        This keeps duplicate dispatching low across scheduler runs.
        """
        if (
            self.db.bind
            and self.db.bind.dialect.name == "sqlite"
            and now.tzinfo is not None
        ):
            now = now.replace(tzinfo=None)

        ids_stmt = (
            select(ScheduledPost.id)
            .where(
                ScheduledPost.status == PostStatus.PENDING,
                ScheduledPost.scheduled_at <= now,
            )
            .order_by(ScheduledPost.scheduled_at.asc(), ScheduledPost.id.asc())
            .limit(limit)
        )
        if self.db.bind and getattr(self.db.bind, "name", "").startswith("postgresql"):
            ids_stmt = ids_stmt.with_for_update(skip_locked=True)

        post_ids = list((await self.db.execute(ids_stmt)).scalars().all())
        if not post_ids:
            return []

        claimed_ids = list(
            (
                await self.db.execute(
                    update(ScheduledPost)
                    .where(
                        ScheduledPost.id.in_(post_ids),
                        ScheduledPost.status == PostStatus.PENDING,
                    )
                    .values(status=PostStatus.QUEUED)
                    .returning(ScheduledPost.id)
                )
            )
            .scalars()
            .all()
        )

        if not claimed_ids:
            return []

        items_stmt = (
            select(ScheduledPost)
            .where(
                ScheduledPost.id.in_(claimed_ids),
                ScheduledPost.status == PostStatus.QUEUED,
            )
            .order_by(ScheduledPost.scheduled_at.asc(), ScheduledPost.id.asc())
        )
        return list((await self.db.execute(items_stmt)).scalars().all())

    async def mark_queued(self, *, post_id: int) -> bool:
        post = await self.get_by_id(post_id=post_id)
        if post is None or post.status != PostStatus.PENDING:
            return False

        post.status = PostStatus.QUEUED
        await self.db.flush()
        return True

    async def get_by_id_and_channel(
        self,
        *,
        post_id: int,
        channel_id: int,
    ) -> ScheduledPost | None:
        stmt = select(ScheduledPost).where(
            ScheduledPost.id == post_id,
            ScheduledPost.channel_id == channel_id,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def get_by_id(
        self,
        *,
        post_id: int,
    ) -> ScheduledPost | None:
        stmt = select(ScheduledPost).where(ScheduledPost.id == post_id)
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def update_pending_post(
        self,
        *,
        post: ScheduledPost,
        content: str | None,
        scheduled_at: datetime | None,
    ) -> ScheduledPost:
        if content is not None:
            post.content = content
        if scheduled_at is not None:
            post.scheduled_at = scheduled_at

        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def cancel(self, *, post: ScheduledPost) -> ScheduledPost:
        post.status = PostStatus.CANCELLED
        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def delete(self, *, post: ScheduledPost) -> None:
        await self.db.delete(post)
        await self.db.flush()

    async def mark_sent(
        self,
        *,
        post_id: int,
        sent_at: datetime,
    ) -> None:
        stmt = (
            update(ScheduledPost)
            .where(ScheduledPost.id == post_id)
            .values(
                status=PostStatus.SENT,
                sent_at=sent_at,
                error_message=None,
            )
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def mark_failed(
        self,
        *,
        post_id: int,
        error_message: str,
    ) -> None:
        stmt = (
            update(ScheduledPost)
            .where(ScheduledPost.id == post_id)
            .values(
                status=PostStatus.FAILED,
                error_message=error_message[:2000],
            )
        )
        await self.db.execute(stmt)
        await self.db.flush()
