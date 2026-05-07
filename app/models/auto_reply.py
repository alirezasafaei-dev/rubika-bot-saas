# app/models/auto_reply.py
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class AutoReply(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "auto_replies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_text: Mapped[str] = mapped_column(String(500), nullable=False)
    reply_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Relationships
    channel: Mapped["Channel"] = relationship(back_populates="auto_replies")
