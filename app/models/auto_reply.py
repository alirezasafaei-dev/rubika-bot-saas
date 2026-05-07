# app/models/auto_reply.py
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.channel import Channel


class AutoReply(Base):
    __tablename__ = "auto_replies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    trigger_text: Mapped[str] = mapped_column(String(500), nullable=False)
    reply_text: Mapped[str] = mapped_column(Text, nullable=False)
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
    channel: Mapped["Channel"] = relationship("Channel", back_populates="auto_replies")
