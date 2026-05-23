import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.channel import Channel


class FilterAction(enum.StrEnum):
    DELETE = "delete"
    WARN = "warn"
    BAN = "ban"
    FLAG = "flag"
    SHADOW_BLOCK = "shadow_block"


class FilterMatchType(enum.StrEnum):
    CONTAINS = "contains"
    REGEX = "regex"


class Filter(Base):
    __tablename__ = "filters"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("channels.id", ondelete="CASCADE"), nullable=False
    )
    pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    match_type: Mapped[FilterMatchType] = mapped_column(
        SQLEnum(
            FilterMatchType,
            name="filter_match_type",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
        default=FilterMatchType.CONTAINS,
    )
    action: Mapped[FilterAction] = mapped_column(
        SQLEnum(
            FilterAction,
            name="filter_action",
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
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

    channel: Mapped["Channel"] = relationship("Channel", back_populates="filters")
