from __future__ import annotations

from redis import Redis  # type: ignore[import-not-found]
from rq import Queue  # type: ignore[import-not-found]

from app.core.config import settings

SCHEDULED_POST_QUEUE = "scheduled_posts"


def get_redis_connection() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=False)


def get_queue(
    *,
    queue_name: str = SCHEDULED_POST_QUEUE,
) -> Queue:
    return Queue(queue_name, connection=get_redis_connection())


def enqueue_scheduled_post(
    *,
    post_id: int,
    queue: Queue | None = None,
) -> str:
    from app.workers.jobs import send_scheduled_post_job

    target = queue or get_queue()
    job = target.enqueue(send_scheduled_post_job, post_id)
    return str(job.id)
