from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook_processing import WebhookEvent


class WebhookEventRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        channel_id: int,
        event_type: str,
        message_id: str | None,
        sender_rubika_user_id: str | None,
        payload: dict[str, Any],
    ) -> WebhookEvent:
        event = WebhookEvent(
            channel_id=channel_id,
            event_type=event_type,
            message_id=message_id,
            sender_rubika_user_id=sender_rubika_user_id,
            payload=payload,
        )
        self.db.add(event)
        await self.db.flush()
        await self.db.refresh(event)
        return event

    async def exists_duplicate(
        self,
        *,
        channel_id: int,
        event_type: str,
        message_id: str | None,
    ) -> bool:
        if message_id is None:
            return False
        stmt = select(WebhookEvent.id).where(
            WebhookEvent.channel_id == channel_id,
            WebhookEvent.event_type == event_type,
            WebhookEvent.message_id == message_id,
        )
        return bool((await self.db.execute(stmt)).first())
