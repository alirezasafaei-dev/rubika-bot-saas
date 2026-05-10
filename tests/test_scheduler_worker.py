from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models.scheduled_post import PostStatus
from app.repositories.scheduled_post_repository import ScheduledPostRepository
from app.scheduler.service import SchedulerService
from app.workers.jobs import send_scheduled_post

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_scheduler_dispatches_due_posts_once(
    db_session,
    test_channel,
    monkeypatch,
):
    repo = ScheduledPostRepository(db_session)
    now = datetime.now(UTC)
    due_post = await repo.create(
        channel_id=test_channel.id,
        content="due",
        scheduled_at=now - timedelta(minutes=1),
    )
    not_due = await repo.create(
        channel_id=test_channel.id,
        content="future",
        scheduled_at=now + timedelta(hours=1),
    )
    await db_session.commit()

    queued = []

    def fake_enqueue(post_id: int, queue=None) -> str:
        queued.append(post_id)
        return f"job-{post_id}"

    monkeypatch.setattr("app.scheduler.service.enqueue_scheduled_post", fake_enqueue)

    service = SchedulerService(db_session)
    enqueued = await service.dispatch_due_posts(now=now, batch_size=10)

    assert enqueued == 1
    assert queued == [due_post.id]
    updated = await repo.get_by_id(post_id=due_post.id)
    assert updated is not None
    assert updated.status == PostStatus.QUEUED
    assert not_due.status == PostStatus.PENDING

    enqueued_again = await service.dispatch_due_posts(now=now, batch_size=10)
    assert enqueued_again == 0


@pytest.mark.asyncio
async def test_worker_marks_post_as_sent(db_session, test_channel, monkeypatch):
    repo = ScheduledPostRepository(db_session)
    now = datetime.now(UTC)
    post = await repo.create(
        channel_id=test_channel.id,
        content="ready",
        scheduled_at=now - timedelta(minutes=1),
    )
    await repo.mark_queued(post_id=post.id)
    await db_session.commit()

    monkeypatch.setattr("app.workers.jobs._session_factory", lambda: db_session)
    result = await send_scheduled_post(post.id)

    assert result is True
    updated = await repo.get_by_id(post_id=post.id)
    assert updated is not None
    assert updated.status == PostStatus.SENT
    assert updated.sent_at is not None
