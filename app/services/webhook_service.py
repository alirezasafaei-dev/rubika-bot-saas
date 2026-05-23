from __future__ import annotations

from datetime import UTC, datetime
import json
import re
from textwrap import dedent

from app.core.config import settings
from app.core.errors import ErrorCode, NotFoundError, UnauthorizedError
from app.integrations import send_text_message
from app.models.auto_reply import AutoReply, AutoReplyMatchType
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
    MENU_TEXT_HELP = "راهنما"
    MENU_TEXT_STATUS = "وضعیت"
    MENU_TEXT_CONTACT = "تماس"
    MENU_TEXT_START = "منوی اصلی"
    INTENT_GREETING = "intent_greeting"
    INTENT_THANKS = "intent_thanks"

    @staticmethod
    def _normalize_text(text: str) -> str:
        return (
            text.strip()
            .lower()
            .replace("ي", "ی")
            .replace("ك", "ک")
            .replace("‌", " ")
            .replace("_", " ")
            .replace("?", "")
            .replace("؟", "")
            .replace("!", "")
        )

    @classmethod
    def _normalize_menu_text(cls, text: str) -> str:
        return cls._normalize_text(text)

    @classmethod
    def _resolve_text_action(cls, text: str) -> str:
        normalized = cls._normalize_menu_text(text)
        text_actions = {
            "راهنما": cls.MENU_HELP,
            "کمک": cls.MENU_HELP,
            "help": cls.MENU_HELP,
            "وضعیت": cls.MENU_STATUS,
            "وضعيت": cls.MENU_STATUS,
            "status": cls.MENU_STATUS,
            "تماس": cls.MENU_CONTACT,
            "پشتیبانی": cls.MENU_CONTACT,
            "پشتيبانی": cls.MENU_CONTACT,
            "ارتباط با پشتیبانی": cls.MENU_CONTACT,
            "تماس با پشتیبانی": cls.MENU_CONTACT,
            "تماس با پشتيبانی": cls.MENU_CONTACT,
            "support": cls.MENU_CONTACT,
            "منوی اصلی": cls.MENU_START,
            "منو اصلی": cls.MENU_START,
            "منوی اصلي": cls.MENU_START,
            "شروع": cls.MENU_START,
            "start": cls.MENU_START,
            "سلام": cls.INTENT_GREETING,
            "سلام ربات": cls.INTENT_GREETING,
            "hi": cls.INTENT_GREETING,
            "hello": cls.INTENT_GREETING,
            "ممنون": cls.INTENT_THANKS,
            "مرسی": cls.INTENT_THANKS,
            "سپاس": cls.INTENT_THANKS,
            "thanks": cls.INTENT_THANKS,
        }
        return text_actions.get(normalized, normalized)

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
        return WebhookService._normalize_text(raw_message or "")

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
            if not item.pattern:
                continue
            if item.match_type.value == "regex":
                try:
                    if re.search(item.pattern, message, re.IGNORECASE):
                        return item
                except re.error:
                    continue
                continue
            if WebhookService._normalize_text(item.pattern) in message:
                return item
        return None

    @staticmethod
    def _reply_matches(message: str, reply: AutoReply) -> bool:
        if not reply.trigger_text:
            return False
        trigger = WebhookService._normalize_text(reply.trigger_text)
        if reply.match_type == AutoReplyMatchType.EXACT:
            return message == trigger
        return trigger in message

    @staticmethod
    def _decode_rich_reply(reply: AutoReply) -> list[str]:
        items: list[str] = []
        if reply.reply_text.strip():
            items.append(reply.reply_text.strip())
        if reply.rich_reply_json:
            try:
                decoded = json.loads(reply.rich_reply_json)
            except json.JSONDecodeError:
                decoded = []
            if isinstance(decoded, list):
                items.extend(
                    item.strip() for item in decoded if isinstance(item, str) and item.strip()
                )
        return items

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
    def _build_no_match_reply(cls) -> tuple[str, dict]:
        return (
            dedent(
                """
                پیام شما را متوجه نشدم.
                برای ادامه یکی از گزینه‌های «راهنما»، «وضعیت» یا «تماس» را بزن، یا /start را بفرست.
                """
            ).strip(),
            cls._inline_back_keypad(),
        )

    @classmethod
    def _build_greeting_reply(cls) -> tuple[str, dict]:
        return (
            "سلام 👋 برای شروع از گزینه‌های راهنما، وضعیت یا تماس استفاده کن.",
            cls._inline_back_keypad(),
        )

    @classmethod
    def _build_thanks_reply(cls) -> tuple[str, dict]:
        return (
            "خواهش می‌کنم 🌷 اگر خواستی می‌توانی از راهنما، وضعیت یا تماس استفاده کنی.",
            cls._inline_back_keypad(),
        )

    @classmethod
    def _build_start_menu(cls) -> tuple[str, dict, dict]:
        bot_name = (settings.rubika_bot_name or settings.app_name).strip() or "ربات"
        text = dedent(
            f"""
            سلام 👋
            به {bot_name} خوش آمدی.
            از منوی زیر استفاده کن:
            • راهنما: نحوه استفاده
            • وضعیت: وضعیت سرویس
            • تماس: مسیر ارتباط با پشتیبانی
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
        normalized = self._normalize_menu_text(message)
        action = button_id or normalized
        if not button_id:
            action = self._resolve_text_action(message)
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
                    • با دکمه‌های پایین می‌توانی سریع‌تر بین گزینه‌ها جابه‌جا شوی.
                    • اگر برای پیام شما پاسخ خودکار تعریف شده باشد، همان پاسخ ارسال می‌شود.
                    • اگر پیام نامشخص باشد، دوباره شما را به مسیر درست هدایت می‌کنم.
                    """
                ).strip(),
                None,
                self._inline_back_keypad(),
                None,
            )
        if action == self.INTENT_GREETING:
            reply_text, inline_keypad = self._build_greeting_reply()
            return reply_text, None, inline_keypad, None
        if action == self.INTENT_THANKS:
            reply_text, inline_keypad = self._build_thanks_reply()
            return reply_text, None, inline_keypad, None
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
                    • دریافت پیام: فعال
                    • ارسال پیام: {"فعال" if settings.rubika_bot_token and settings.rubika_send_endpoint else "نیازمند تنظیمات"}
                    • پاسخ‌خودکارهای فعال: {len(active_auto_replies)}
                    • فیلترهای فعال: {len(active_filters)}
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
                    • برای برگشت به منوی اصلی، دکمه «بازگشت» را بزن.
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

    async def _send_auto_reply_flow(
        self,
        *,
        channel_id: int,
        rubika_channel_id: str,
        reply: AutoReply,
    ) -> None:
        current = reply
        visited: set[int] = set()
        depth = 0
        while current is not None and current.id not in visited and depth < 5:
            visited.add(current.id)
            for item in self._decode_rich_reply(current):
                await self._send_bot_reply(
                    channel_id=channel_id,
                    rubika_channel_id=rubika_channel_id,
                    text=item,
                )
            if current.next_step_id is None:
                break
            current = await self.auto_reply_repo.get_by_id_and_channel(
                rule_id=current.next_step_id,
                channel_id=channel_id,
            )
            if current is None or not current.is_active:
                break
            depth += 1

    async def _record_processing_error(
        self,
        *,
        event_id: int,
        channel_id: int,
        payload: dict,
        reason: str,
        auto_reply_rule_id: int | None = None,
    ) -> None:
        await self._record_message_outcome(
            event_id=event_id,
            channel_id=channel_id,
            outcome=ProcessingOutcome.ERROR,
            payload=payload,
            auto_reply_rule_id=auto_reply_rule_id,
            reason=reason[:500],
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
        button_id = payload.get("button_id")
        filters = await self.filter_repo.list_active_by_channel(channel_id=channel_id)
        matched_filter = self._find_filter_match(normalized_message, filters)
        if matched_filter is not None and normalized_message:
            if matched_filter.action in {
                FilterAction.DELETE,
                FilterAction.BAN,
                FilterAction.SHADOW_BLOCK,
            }:
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
                "reason": "flagged" if matched_filter.action == FilterAction.FLAG else "warning",
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
            try:
                await self._send_bot_reply(
                    channel_id=channel_id,
                    rubika_channel_id=(await self._require_channel(channel_id)).rubika_channel_id,
                    text=reply_text,
                    chat_keypad=chat_keypad,
                    inline_keypad=inline_keypad,
                    chat_keypad_type=chat_keypad_type,
                )
            except RuntimeError as exc:
                await self._record_processing_error(
                    event_id=event.id,
                    channel_id=channel_id,
                    payload=payload,
                    reason=f"menu_reply_send_failed: {exc}",
                )
                await self.db.commit()
                return {"accepted": True, "reason": "send_failed"}
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
            if self._reply_matches(normalized_message, reply):
                try:
                    await self._send_auto_reply_flow(
                        channel_id=channel_id,
                        rubika_channel_id=(await self._require_channel(channel_id)).rubika_channel_id,
                        reply=reply,
                    )
                except RuntimeError as exc:
                    await self._record_processing_error(
                        event_id=event.id,
                        channel_id=channel_id,
                        payload=payload,
                        auto_reply_rule_id=reply.id,
                        reason=f"auto_reply_send_failed: {exc}",
                    )
                    await self.db.commit()
                    return {"accepted": True, "reason": "send_failed"}
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
        if normalized_message:
            reply_text, inline_keypad = self._build_no_match_reply()
            try:
                await self._send_bot_reply(
                    channel_id=channel_id,
                    rubika_channel_id=(await self._require_channel(channel_id)).rubika_channel_id,
                    text=reply_text,
                    inline_keypad=inline_keypad,
                )
            except RuntimeError:
                pass
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
