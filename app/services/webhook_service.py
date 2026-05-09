from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.errors import ErrorCode, NotFoundError
from app.repositories.channel_repository import ChannelRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.channel import Channel


class WebhookService:
    def __init__(self, db_session: AsyncSession) -> None:
        self.db = db_session
        self.channel_repo = ChannelRepository(db_session)

    async def _require_channel(self, channel_id: int) -> Channel:
        channel = await self.channel_repo.get_by_id(channel_id)
        if channel is None:
            raise NotFoundError(
                error_code=ErrorCode.NOT_FOUND,
                message="Channel not found",
            )
        return channel

    def _validate_secret(self, payload_secret: str | None) -> None:
        expected_secret = settings.webhook_secret
        if not expected_secret:
            return
        if payload_secret is None or payload_secret != expected_secret:
            raise PermissionError("Invalid webhook secret")

    async def process_message_event(
        self, *, channel_id: int, secret: str | None
    ) -> dict:
        await self._require_channel(channel_id)
        self._validate_secret(secret)

        now = datetime.now(UTC)
        return {
            "accepted": True,
            "event": "message_received",
            "processed_at": now.isoformat(),
        }

    async def process_delivery_event(
        self, *, channel_id: int, secret: str | None
    ) -> dict:
        await self._require_channel(channel_id)
        self._validate_secret(secret)

        now = datetime.now(UTC)
        return {
            "accepted": True,
            "event": "delivery_result",
            "processed_at": now.isoformat(),
        }
