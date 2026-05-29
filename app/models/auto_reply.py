from __future__ import annotations

import enum
import json
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.channel import Channel


class AutoReplyMatchType(enum.StrEnum):
    CONTAINS = "contains"
    EXACT = "exact"


class AutoReply(Base):
    __tablename__ = "auto_replies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    trigger_text: Mapped[str] = mapped_column(String(500), nullable=False)
    match_type: Mapped[AutoReplyMatchType] = mapped_column(
        SQLEnum(
            AutoReplyMatchType,
            name="auto_reply_match_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=AutoReplyMatchType.CONTAINS,
    )
    reply_text: Mapped[str] = mapped_column(Text, nullable=False)
    rich_reply_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_step_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("auto_replies.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    channel: Mapped[Channel] = relationship("Channel", back_populates="auto_replies")
    next_step: Mapped[AutoReply | None] = relationship(
        "AutoReply",
        remote_side="AutoReply.id",
        foreign_keys=[next_step_id],
        post_update=True,
    )

    @property
    def rich_reply(self) -> list[str] | None:
        if not self.rich_reply_json:
            return None
        try:
            decoded = json.loads(self.rich_reply_json)
        except json.JSONDecodeError:
            return None
        if not isinstance(decoded, list):
            return None
        return [item for item in decoded if isinstance(item, str)]
