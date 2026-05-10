from __future__ import annotations

from rq import Queue, Worker  # type: ignore[import-not-found]

from app.workers.queue import SCHEDULED_POST_QUEUE, get_redis_connection


def main() -> None:
    connection = get_redis_connection()
    queue = Queue(SCHEDULED_POST_QUEUE, connection=connection)
    worker = Worker([queue], connection=connection)
    worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()
