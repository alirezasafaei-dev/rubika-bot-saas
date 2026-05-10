from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.integrations import send_text_message
from app.models.scheduled_post import PostStatus
from app.repositories.channel_repository import ChannelRepository
from app.repositories.scheduled_post_repository import ScheduledPostRepository

logger = logging.getLogger(__name__)


async def send_scheduled_post(post_id: int) -> bool:
    async with _session_factory() as db:
        repo = ScheduledPostRepository(db)
        channel_repo = ChannelRepository(db)
        post = await repo.get_by_id(post_id=post_id)
        if post is None:
            logger.warning("Scheduled post %s not found", post_id)
            return False

        if post.status not in (PostStatus.QUEUED, PostStatus.PENDING):
            logger.info("Scheduled post %s skipped: status=%s", post_id, post.status)
            return False

        now = datetime.now(UTC)
        if post.scheduled_at.tzinfo is None:
            now = now.replace(tzinfo=None)
        if post.scheduled_at > now:
            logger.info("Scheduled post %s not ready yet", post_id)
            return False

        try:
            channel = await channel_repo.get_by_id(post.channel_id)
            if channel is None:
                raise RuntimeError(f"Channel {post.channel_id} not found")

            result = await send_text_message(channel.rubika_channel_id, post.content)
            if not result.ok:
                raise RuntimeError(result.error or "rubika send failed")

            await repo.mark_sent(post_id=post_id, sent_at=now)
            await db.commit()
            logger.info("Scheduled post %s marked sent", post_id)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            await db.rollback()
            await repo.mark_failed(post_id=post_id, error_message=str(exc))
            await db.commit()
            logger.exception("Scheduled post %s failed: %s", post_id, exc)
            return False


def send_scheduled_post_job(post_id: int) -> bool:
    return asyncio.run(send_scheduled_post(post_id))


def _session_factory() -> AsyncSession:
    return AsyncSessionLocal()
