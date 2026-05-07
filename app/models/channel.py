# app/models/channel.py
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.auto_reply import AutoReply
    from app.models.filter import Filter
    from app.models.scheduled_post import ScheduledPost
    from app.models.workspace import Workspace


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    workspace_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False
    )
    rubika_channel_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
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
    workspace: Mapped["Workspace"] = relationship(
        "Workspace", back_populates="channels"
    )
    scheduled_posts: Mapped[list["ScheduledPost"]] = relationship(
        "ScheduledPost", back_populates="channel", cascade="all, delete-orphan"
    )
    auto_replies: Mapped[list["AutoReply"]] = relationship(
        "AutoReply", back_populates="channel", cascade="all, delete-orphan"
    )
    filters: Mapped[list["Filter"]] = relationship(
        "Filter", back_populates="channel", cascade="all, delete-orphan"
    )
