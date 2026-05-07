# app/models/filter.py
from __future__ import annotations

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SoftDeleteMixin, TimestampMixin


class Filter(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), nullable=False, index=True)
    pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    action: Mapped[str] = mapped_column(
        Enum("delete", "warn", name="filter_action_enum"), nullable=False, server_default="delete"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")

    # Relationships
    channel: Mapped["Channel"] = relationship(back_populates="filters")
