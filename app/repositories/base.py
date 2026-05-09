# app/repositories/base.py
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository[ModelType]:
    """Generic async repository for SQLAlchemy models."""

    def __init__(self, model: type[ModelType], session: AsyncSession) -> None:
        self.model = model
        self.session = session

    # ── Read ──────────────────────────────────────────────────────────

    async def get_by_id(self, id_: int) -> ModelType | None:
        stmt: Select[tuple[ModelType]] = select(self.model).where(
            self.model.id == id_  # type: ignore[attr-defined]
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_one_by(self, **filters: Any) -> ModelType | None:
        """Fetch first record matching all supplied filters."""
        stmt = select(self.model)
        for attr, value in filters.items():
            stmt = stmt.where(getattr(self.model, attr) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        page: int = 1,
        limit: int = 20,
        order_by: Any | None = None,
        **filters: Any,
    ) -> list[ModelType]:
        """Paginated list with optional filters.

        Page is 1-based.  If *order_by* is ``None`` the default is
        ``self.model.id`` ascending.
        """
        stmt = select(self.model)
        for attr, value in filters.items():
            stmt = stmt.where(getattr(self.model, attr) == value)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        else:
            stmt = stmt.order_by(self.model.id)  # type: ignore[attr-defined]
        stmt = stmt.offset((page - 1) * limit).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, **filters: Any) -> int:
        """Count rows matching supplied filters."""
        stmt = select(func.count(self.model.id))  # type: ignore[attr-defined]
        for attr, value in filters.items():
            stmt = stmt.where(getattr(self.model, attr) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    # ── Write ─────────────────────────────────────────────────────────

    async def create(self, **kwargs: Any) -> ModelType:
        """Build, persist and return a new instance."""
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType, **kwargs: Any) -> ModelType:
        """Apply field updates to an existing instance."""
        for key, value in kwargs.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def soft_delete(self, obj: ModelType) -> None:
        """Set ``deleted_at`` on models that support it."""
        if hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.now(UTC)
            await self.session.flush()

    async def delete(self, obj: ModelType) -> None:
        """Hard-delete from database."""
        await self.session.delete(obj)
        await self.session.flush()

    # ── Utilities ─────────────────────────────────────────────────────

    async def save(self) -> None:
        """Flush pending changes without committing."""
        await self.session.flush()

    async def refresh(self, obj: ModelType) -> None:
        await self.session.refresh(obj)

    async def execute(self, stmt: Any) -> Any:
        return await self.session.execute(stmt)
