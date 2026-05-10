from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.auto_reply import AutoReply
    from app.models.channel import Channel
    from app.models.filter import Filter


class ProcessingOutcome(enum.StrEnum):
    DUPLICATE = "duplicate"
    FILTER_BLOCKED = "filter_blocked"
    AUTO_REPLIED = "auto_replied"
    NO_MATCH = "no_match"
    DELIVERY_RESULT = "delivery_result"
    ERROR = "error"


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    message_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sender_rubika_user_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    channel: Mapped[Channel] = relationship("Channel", back_populates="webhook_events")


class MessageProcessingLog(Base):
    __tablename__ = "message_processing_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_id: Mapped[int] = mapped_column(
        ForeignKey("webhook_events.id", ondelete="SET NULL"), nullable=True, index=True
    )
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filter_rule_id: Mapped[int | None] = mapped_column(
        ForeignKey("filters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    auto_reply_rule_id: Mapped[int | None] = mapped_column(
        ForeignKey("auto_replies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    outcome: Mapped[ProcessingOutcome] = mapped_column(
        SQLEnum(ProcessingOutcome, name="processing_outcome"),
        nullable=False,
        index=True,
    )
    message_excerpt: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    channel: Mapped[Channel] = relationship(
        "Channel", back_populates="message_processing_logs"
    )
    filter_rule: Mapped[Filter | None] = relationship("Filter")
    auto_reply_rule: Mapped[AutoReply | None] = relationship("AutoReply")
