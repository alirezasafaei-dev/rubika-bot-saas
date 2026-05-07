# app/db/base.py
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all models."""

    pass


class TimestampMixin:
    """Mixin for created_at and updated_at."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin for soft delete."""

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)


# Import all models for Alembic autogenerate
from app.models.user import User  # noqa: E402, F401
from app.models.workspace import Workspace, WorkspaceMember  # noqa: E402, F401
from app.models.channel import Channel  # noqa: E402, F401
from app.models.scheduled_post import ScheduledPost  # noqa: E402, F401
from app.models.auto_reply import AutoReply  # noqa: E402, F401
from app.models.filter import Filter  # noqa: E402, F401
from app.models.webhook import Webhook, WebhookDelivery  # noqa: E402, F401
from app.models.report import Report  # noqa: E402, F401
