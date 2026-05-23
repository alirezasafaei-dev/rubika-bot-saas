from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from app.models.scheduled_post import PostStatus, ScheduledPost
from app.models.webhook_processing import MessageProcessingLog, ProcessingOutcome

pytestmark = pytest.mark.asyncio


async def test_workspace_summary(
    async_client,
    auth_headers,
    workspace,
    channel,
    workspace_member,
    db_session,
):
    now = datetime.now(UTC)
    db_session.add_all(
        [
            ScheduledPost(
                channel_id=channel.id,
                content="created",
                status=PostStatus.PENDING,
                scheduled_at=now,
                created_at=now,
            ),
            ScheduledPost(
                channel_id=channel.id,
                content="sent",
                status=PostStatus.SENT,
                scheduled_at=now,
                created_at=now,
            ),
            ScheduledPost(
                channel_id=channel.id,
                content="failed",
                status=PostStatus.FAILED,
                scheduled_at=now,
                created_at=now,
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.AUTO_REPLIED,
                auto_reply_rule_id=None,
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.FILTER_BLOCKED,
                filter_rule_id=None,
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.DELIVERY_RESULT,
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.ERROR,
            ),
        ]
    )
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/reports/summary",
        params={
            "from": (now - timedelta(days=1)).isoformat(),
            "to": now.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == workspace.id
    assert data["summary"]["created_posts"] == 3
    assert data["summary"]["sent_posts"] == 1
    assert data["summary"]["failed_posts"] == 1
    assert data["summary"]["auto_replies_sent"] == 1
    assert data["summary"]["deleted_messages"] == 1
    assert data["summary"]["webhook_delivery_results"] == 1
    assert data["summary"]["webhook_processing_errors"] == 1


async def test_channel_summary(
    async_client,
    auth_headers,
    workspace,
    channel,
    workspace_member,
    db_session,
):
    now = datetime.now(UTC)
    db_session.add_all(
        [
            ScheduledPost(
                channel_id=channel.id,
                content="created",
                status=PostStatus.PENDING,
                scheduled_at=now,
                created_at=now,
            ),
            ScheduledPost(
                channel_id=channel.id,
                content="sent",
                status=PostStatus.SENT,
                scheduled_at=now,
                created_at=now,
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.AUTO_REPLIED,
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.FILTER_BLOCKED,
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.ERROR,
            ),
        ]
    )
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/channels/{channel.id}/reports/summary",
        params={
            "from": (now - timedelta(days=1)).isoformat(),
            "to": now.isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == workspace.id
    assert data["channel_id"] == channel.id
    assert data["summary"]["created_posts"] == 2
    assert data["summary"]["sent_posts"] == 1
    assert data["summary"]["webhook_processing_errors"] == 1


async def test_daily_report_returns_buckets(
    async_client,
    auth_headers,
    workspace,
    channel,
    workspace_member,
    db_session,
):
    start = datetime.now(UTC).replace(hour=10, minute=0, second=0, microsecond=0)
    db_session.add_all(
        [
            ScheduledPost(
                channel_id=channel.id,
                content="today",
                status=PostStatus.SENT,
                scheduled_at=start,
                created_at=start,
            ),
            ScheduledPost(
                channel_id=channel.id,
                content="yesterday",
                status=PostStatus.FAILED,
                scheduled_at=start - timedelta(days=1),
                created_at=start - timedelta(days=1),
            ),
            MessageProcessingLog(
                channel_id=channel.id,
                outcome=ProcessingOutcome.ERROR,
                created_at=start,
            ),
        ]
    )
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/reports/daily?days=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["workspace_id"] == workspace.id
    assert len(data["items"]) == 2
    assert data["items"][-1]["webhook_processing_errors"] >= 1


async def test_reports_invalid_date_range(
    async_client,
    auth_headers,
    workspace,
    channel,
    workspace_member,
):
    now = datetime.now(UTC)
    response = await async_client.get(
        f"/api/v1/workspaces/{workspace.id}/reports/summary",
        params={
            "from": now.isoformat(),
            "to": (now - timedelta(days=1)).isoformat(),
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
