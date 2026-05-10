from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.repositories.scheduled_post_repository import ScheduledPostRepository
from app.workers.queue import SCHEDULED_POST_QUEUE, enqueue_scheduled_post, get_queue


class SchedulerService:
    def __init__(self, db):
        self.db = db
        self.repo = ScheduledPostRepository(db)

    async def dispatch_due_posts(
        self,
        *,
        now: datetime | None = None,
        batch_size: int = 100,
        queue: Any | None = None,
    ) -> int:
        now = now or datetime.now(UTC)

        target_queue = queue or get_queue(queue_name=SCHEDULED_POST_QUEUE)

        posts = await self.repo.claim_due_posts(now=now, limit=batch_size)
        if not posts:
            return 0

        enqueued = 0
        for post in posts:
            enqueue_scheduled_post(post_id=post.id, queue=target_queue)
            enqueued += 1

        await self.db.commit()
        return enqueued
