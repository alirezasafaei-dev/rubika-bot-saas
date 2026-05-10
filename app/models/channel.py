# app/models/channel.py
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workspaces.id"), nullable=False
    )
    rubika_channel_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # relationships
    workspace = relationship("Workspace", back_populates="channels")
    auto_replies: Mapped[list["AutoReply"]] = relationship(
        "AutoReply", back_populates="channel", cascade="all, delete-orphan"
    )
    scheduled_posts: Mapped[list["ScheduledPost"]] = relationship(
        "ScheduledPost", back_populates="channel", cascade="all, delete-orphan"
    )
    filters: Mapped[list["Filter"]] = relationship(
        "Filter", back_populates="channel", cascade="all, delete-orphan"
    )
    webhook_events: Mapped[list["WebhookEvent"]] = relationship(
        "WebhookEvent", back_populates="channel", cascade="all, delete-orphan"
    )
    message_processing_logs: Mapped[list["MessageProcessingLog"]] = relationship(
        "MessageProcessingLog",
        back_populates="channel",
        cascade="all, delete-orphan",
    )


if TYPE_CHECKING:
    # Type checking imports for related models
    from app.models.auto_reply import AutoReply
    from app.models.filter import Filter
    from app.models.scheduled_post import ScheduledPost
    from app.models.webhook_processing import MessageProcessingLog, WebhookEvent
