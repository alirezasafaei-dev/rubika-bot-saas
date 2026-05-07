# app/models/report.py
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False, index=True
    )
    channel_id: Mapped[int | None] = mapped_column(
        ForeignKey("channels.id", ondelete="SET NULL"), nullable=True, index=True
    )
    report_type: Mapped[str] = mapped_column(
        Enum("daily", "weekly", "monthly", name="report_type_enum"), nullable=False, index=True
    )
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    total_messages: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_members: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_posts: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_replies: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_filtered: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
