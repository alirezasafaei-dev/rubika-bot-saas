from __future__ import annotations

from datetime import UTC, datetime
from textwrap import dedent

from app.core.config import settings
from app.core.errors import ErrorCode, NotFoundError, UnauthorizedError
from app.integrations import send_text_message
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
    MENU_HELP = "menu_help"
    MENU_STATUS = "menu_status"
    MENU_CONTACT = "menu_contact"
    MENU_BACK = "menu_back"
    MENU_START = "menu_start"

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

    @staticmethod
    def _inline_back_keypad() -> dict:
        return {
            "rows": [
                {
                    "buttons": [
                        {
                            "id": WebhookService.MENU_BACK,
                            "type": "Simple",
                            "button_text": "بازگشت",
                        }
                    ]
                }
            ]
        }

    @classmethod
    def _build_start_menu(cls) -> tuple[str, dict, dict]:
        bot_name = (settings.rubika_bot_name or settings.app_name).strip() or "ربات"
        text = dedent(
            f"""
            سلام 👋
            به {bot_name} خوش آمدی.
            از دکمه‌ها برای دیدن راهنما، وضعیت سرویس و مسیر تماس استفاده کن.
            """
        ).strip()
        chat_keypad = {
            "rows": [
                {
                    "buttons": [
                        {"id": cls.MENU_HELP, "type": "Simple", "button_text": "راهنما"},
                        {"id": cls.MENU_STATUS, "type": "Simple", "button_text": "وضعیت"},
                    ]
                },
                {
                    "buttons": [
                        {"id": cls.MENU_CONTACT, "type": "Simple", "button_text": "تماس"}
                    ]
                },
            ],
            "resize_keyboard": True,
            "on_time_keyboard": False,
        }
        inline_keypad = {
            "rows": [
                {
                    "buttons": [
                        {"id": cls.MENU_HELP, "type": "Simple", "button_text": "راهنما"},
                        {"id": cls.MENU_STATUS, "type": "Simple", "button_text": "وضعیت"},
                    ]
                },
                {
                    "buttons": [
                        {"id": cls.MENU_CONTACT, "type": "Simple", "button_text": "تماس"},
                        {"id": cls.MENU_START, "type": "Simple", "button_text": "منوی اصلی"},
                    ]
                },
            ]
        }
        return text, chat_keypad, inline_keypad

    async def _menu_reply(
        self,
        *,
        channel_id: int,
        message: str,
        button_id: str | None,
    ) -> tuple[str, dict | None, dict | None, str | None] | None:
        normalized = message.strip().lower()
        action = button_id or normalized
        if normalized.startswith("/start") or action in {
            self.MENU_BACK,
            self.MENU_START,
        }:
            text, chat_keypad, inline_keypad = self._build_start_menu()
            return text, chat_keypad, inline_keypad, "New"
        if normalized.startswith("/help") or action == self.MENU_HELP:
            return (
                dedent(
                    """
                    راهنما:
                    • /start منوی اصلی را باز می‌کند.
                    • راهنما، وضعیت و تماس از دکمه‌ها هم در دسترس‌اند.
                    • اگر برای پیام شما auto-reply تعریف شده باشد، همان پاسخ ارسال می‌شود.
                    """
                ).strip(),
                None,
                self._inline_back_keypad(),
                None,
            )
        if action == self.MENU_STATUS:
            channel = await self._require_channel(channel_id)
            active_auto_replies = await self.auto_reply_repo.list_active_by_channel(
                channel_id=channel_id
            )
            active_filters = await self.filter_repo.list_active_by_channel(
                channel_id=channel_id
            )
            return (
                dedent(
                    f"""
                    وضعیت سرویس:
                    • کانال: {channel.name}
                    • webhook: فعال
                    • ارسال پیام: {"فعال" if settings.rubika_bot_token and settings.rubika_send_endpoint else "نیازمند تنظیمات"}
                    • پاسخ‌خودکار فعال: {len(active_auto_replies)}
                    • فیلتر فعال: {len(active_filters)}
                    """
                ).strip(),
                None,
                self._inline_back_keypad(),
                None,
            )
        if action == self.MENU_CONTACT:
            contact = (settings.rubika_support_contact or "").strip()
            contact_line = (
                f"• مسیر تماس: {contact}" if contact else "• مسیر تماس هنوز در تنظیمات ثبت نشده است."
            )
            return (
                dedent(
                    f"""
                    تماس و پشتیبانی:
                    {contact_line}
                    • اگر نیاز به بازگشت داری، دکمه «بازگشت» را بزن.
                    """
                ).strip(),
                None,
                self._inline_back_keypad(),
                None,
            )
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

    async def _send_bot_reply(
        self,
        *,
        channel_id: int,
        rubika_channel_id: str,
        text: str,
        chat_keypad: dict | None = None,
        inline_keypad: dict | None = None,
        chat_keypad_type: str | None = None,
    ) -> None:
        result = await send_text_message(
            rubika_channel_id,
            text,
            chat_keypad=chat_keypad,
            inline_keypad=inline_keypad,
            chat_keypad_type=chat_keypad_type,
        )
        if not result.ok:
            raise RuntimeError(result.error or f"failed to send reply for {channel_id}")

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
        button_id = payload.get("button_id")
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
        menu_reply = await self._menu_reply(
            channel_id=channel_id,
            message=normalized_message,
            button_id=button_id if isinstance(button_id, str) else None,
        )
        if menu_reply is not None:
            reply_text, chat_keypad, inline_keypad, chat_keypad_type = menu_reply
            await self._send_bot_reply(
                channel_id=channel_id,
                rubika_channel_id=(await self._require_channel(channel_id)).rubika_channel_id,
                text=reply_text,
                chat_keypad=chat_keypad,
                inline_keypad=inline_keypad,
                chat_keypad_type=chat_keypad_type,
            )
            await self._record_message_outcome(
                event_id=event.id,
                channel_id=channel_id,
                outcome=ProcessingOutcome.AUTO_REPLIED,
                payload=payload,
                reason="menu_reply",
            )
            await self.db.commit()
            return {
                "accepted": True,
                "reason": "menu_reply",
            }
        for reply in auto_replies:
            if not reply.trigger_text:
                continue
            if reply.trigger_text.lower() in normalized_message:
                await self._send_bot_reply(
                    channel_id=channel_id,
                    rubika_channel_id=(await self._require_channel(channel_id)).rubika_channel_id,
                    text=reply.reply_text,
                )
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
