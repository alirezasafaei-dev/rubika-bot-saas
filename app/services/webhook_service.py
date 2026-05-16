from __future__ import annotations

from datetime import UTC, datetime

from app.core.config import settings
from app.core.errors import ErrorCode, NotFoundError, UnauthorizedError
from app.models.filter import Filter, FilterAction
from app.models.webhook_processing import ProcessingOutcome
from app.repositories.auto_reply_repository import AutoReplyRepository
from app.repositories.channel_repository import ChannelRepository
from app.repositories.filter_repository import FilterRepository
from app.repositories.message_processing_log_repository import (
    MessageProcessingLogRepository,
)
from app.repositories.webhook_event_repository import WebhookEventRepository


class WebhookService:
    def __init__(self, db_session) -> None:
        self.db = db_session
        self.channel_repo = ChannelRepository(db_session)
        self.filter_repo = FilterRepository(db_session)
        self.auto_reply_repo = AutoReplyRepository(db_session)
        self.event_repo = WebhookEventRepository(db_session)
        self.log_repo = MessageProcessingLogRepository(db_session)

    async def _require_channel(self, channel_id: int):
        channel = await self.channel_repo.get_by_id(channel_id)
        if channel is None:
            raise NotFoundError(
                error_code=ErrorCode.CHANNEL_NOT_FOUND,
                message="Channel not found",
            )
        return channel

    async def _require_channel_by_rubika_id(self, rubika_channel_id: str):
        channel = await self.channel_repo.get_by_rubika_channel_id(rubika_channel_id)
        if channel is None:
            raise NotFoundError(
                error_code=ErrorCode.CHANNEL_NOT_FOUND,
                message="Channel not found",
            )
        return channel

    def _validate_secret(self, payload_secret: str | None) -> None:
        expected_secret = settings.webhook_secret
        if not expected_secret:
            return
        if payload_secret != expected_secret:
            raise UnauthorizedError(ErrorCode.UNAUTHORIZED, "Invalid webhook secret")

    @staticmethod
    def _message_for_match(raw_message: str | None) -> str:
        return (raw_message or "").strip().lower()

    @staticmethod
    def _excerpt(message: str | None) -> str | None:
        if not message:
            return None
        text = message.strip()
        if not text:
            return None
        return text[:250]

    @staticmethod
    def _find_filter_match(message: str, filters: list[Filter]) -> Filter | None:
        for item in filters:
            if item.pattern and item.pattern.lower() in message:
                return item
        return None

    async def _record_message_outcome(
        self,
        *,
        event_id: int,
        channel_id: int,
        outcome: ProcessingOutcome,
        payload: dict,
        filter_rule_id: int | None = None,
        auto_reply_rule_id: int | None = None,
        reason: str | None = None,
    ) -> None:
        await self.log_repo.create(
            event_id=event_id,
            channel_id=channel_id,
            outcome=outcome,
            filter_rule_id=filter_rule_id,
            auto_reply_rule_id=auto_reply_rule_id,
            message_excerpt=self._excerpt(payload.get("message")),
            reason=reason,
        )

    async def process_message_event(
        self, *, channel_id: int, secret: str | None, payload: dict
    ) -> dict:
        await self._require_channel(channel_id)
        self._validate_secret(secret)

        message_id = payload.get("message_id")
        if await self.event_repo.exists_duplicate(
            channel_id=channel_id,
            event_type="message_received",
            message_id=message_id,
        ):
            return {"accepted": False, "reason": "duplicate"}

        event = await self.event_repo.create(
            channel_id=channel_id,
            event_type="message_received",
            message_id=message_id,
            sender_rubika_user_id=payload.get("sender_rubika_user_id"),
            payload=payload,
        )

        message = payload.get("message")
        normalized_message = self._message_for_match(message)
        filters = await self.filter_repo.list_active_by_channel(channel_id=channel_id)
        matched_filter = self._find_filter_match(normalized_message, filters)
        if matched_filter is not None and normalized_message:
            if matched_filter.action in {FilterAction.DELETE, FilterAction.BAN}:
                await self._record_message_outcome(
                    event_id=event.id,
                    channel_id=channel_id,
                    outcome=ProcessingOutcome.FILTER_BLOCKED,
                    payload=payload,
                    filter_rule_id=matched_filter.id,
                    reason=f"blocked by {matched_filter.action.value}",
                )
                await self.db.commit()
                return {
                    "accepted": True,
                    "reason": "filtered",
                }
            await self._record_message_outcome(
                event_id=event.id,
                channel_id=channel_id,
                outcome=ProcessingOutcome.NO_MATCH,
                payload=payload,
                filter_rule_id=matched_filter.id,
                reason=f"warned by {matched_filter.action.value}",
            )
            await self.db.commit()
            return {
                "accepted": True,
                "reason": "warning",
            }

        auto_replies = await self.auto_reply_repo.list_active_by_channel(
            channel_id=channel_id
        )
        for reply in auto_replies:
            if not reply.trigger_text:
                continue
            if reply.trigger_text.lower() in normalized_message:
                await self._record_message_outcome(
                    event_id=event.id,
                    channel_id=channel_id,
                    outcome=ProcessingOutcome.AUTO_REPLIED,
                    payload=payload,
                    auto_reply_rule_id=reply.id,
                    reason="auto_reply_matched",
                )
                await self.db.commit()
                return {
                    "accepted": True,
                    "reason": "auto_reply_triggered",
                }

        await self._record_message_outcome(
            event_id=event.id,
            channel_id=channel_id,
            outcome=ProcessingOutcome.NO_MATCH,
            payload=payload,
            reason="no_match",
        )
        await self.db.commit()
        return {"accepted": True, "reason": "message_processed"}

    async def process_message_event_from_rubika_channel(
        self, *, rubika_channel_id: str, secret: str | None, payload: dict
    ) -> dict:
        channel = await self._require_channel_by_rubika_id(rubika_channel_id)
        return await self.process_message_event(
            channel_id=channel.id,
            secret=secret,
            payload=payload,
        )

    async def process_delivery_event(
        self, *, channel_id: int, secret: str | None, payload: dict
    ) -> dict:
        await self._require_channel(channel_id)
        self._validate_secret(secret)

        event = await self.event_repo.create(
            channel_id=channel_id,
            event_type="delivery_result",
            message_id=payload.get("message_id"),
            sender_rubika_user_id=payload.get("sender_rubika_user_id"),
            payload=payload,
        )
        await self._record_message_outcome(
            event_id=event.id,
            channel_id=channel_id,
            outcome=ProcessingOutcome.DELIVERY_RESULT,
            payload=payload,
            reason="delivery_result_received",
        )
        await self.db.commit()

        now = datetime.now(UTC)
        return {
            "accepted": True,
            "event": "delivery_result",
            "processed_at": now.isoformat(),
        }

    async def process_delivery_event_from_rubika_channel(
        self, *, rubika_channel_id: str, secret: str | None, payload: dict
    ) -> dict:
        channel = await self._require_channel_by_rubika_id(rubika_channel_id)
        return await self.process_delivery_event(
            channel_id=channel.id,
            secret=secret,
            payload=payload,
        )
