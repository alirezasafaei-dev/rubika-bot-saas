from __future__ import annotations

import importlib
from typing import Any

from app.core.config import settings

SCHEDULED_POST_QUEUE = "scheduled_posts"


def get_redis_connection() -> Any:
    redis_module = importlib.import_module("redis")
    return redis_module.Redis.from_url(settings.redis_url, decode_responses=False)


def redis_ping() -> bool:
    """Return True when Redis is reachable for worker and scheduler traffic."""
    return bool(get_redis_connection().ping())


def get_queue(
    *,
    queue_name: str = SCHEDULED_POST_QUEUE,
) -> Any:
    rq_module = importlib.import_module("rq")
    return rq_module.Queue(queue_name, connection=get_redis_connection())


def enqueue_scheduled_post(
    *,
    post_id: int,
    queue: Any | None = None,
) -> str:
    from app.workers.jobs import send_scheduled_post_job

    target = queue or get_queue()
    job = target.enqueue(send_scheduled_post_job, post_id)
    return str(job.id)
