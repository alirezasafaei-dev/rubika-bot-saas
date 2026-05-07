# app/models/channel.py
from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class Channel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rubika_channel_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Relationships
    workspace: Mapped["Workspace"] = relationship(back_populates="channels")
    scheduled_posts: Mapped[list["ScheduledPost"]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )
    auto_replies: Mapped[list["AutoReply"]] = relationship(back_populates="channel", cascade="all, delete-orphan")
    filters: Mapped[list["Filter"]] = relationship(back_populates="channel", cascade="all, delete-orphan")
