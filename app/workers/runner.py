from __future__ import annotations

import importlib

from app.workers.queue import SCHEDULED_POST_QUEUE, get_redis_connection


def main() -> None:
    connection = get_redis_connection()
    rq_module = importlib.import_module("rq")
    Queue = rq_module.Queue
    Worker = rq_module.Worker

    queue = Queue(SCHEDULED_POST_QUEUE, connection=connection)
    worker = Worker([queue], connection=connection)
    worker.work(with_scheduler=False)


if __name__ == "__main__":
    main()
