from __future__ import annotations

import asyncio
import logging
import os

from app.db.session import AsyncSessionLocal
from app.scheduler.service import SchedulerService

logger = logging.getLogger(__name__)


async def _tick(batch_size: int) -> int:
    async with AsyncSessionLocal() as db:
        service = SchedulerService(db)
        return await service.dispatch_due_posts(batch_size=batch_size)


async def run_loop(interval_seconds: int = 30, batch_size: int = 100) -> None:
    while True:
        enqueued = await _tick(batch_size=batch_size)
        logger.info("Scheduler dispatched %s post(s)", enqueued)
        await asyncio.sleep(interval_seconds)


def main() -> None:
    interval_seconds = int(os.getenv("SCHEDULER_INTERVAL_SECONDS", "30"))
    batch_size = int(os.getenv("SCHEDULER_BATCH_SIZE", "100"))
    logger.info(
        "Starting scheduler with interval=%s seconds batch_size=%s",
        interval_seconds,
        batch_size,
    )
    asyncio.run(run_loop(interval_seconds=interval_seconds, batch_size=batch_size))


if __name__ == "__main__":
    main()
