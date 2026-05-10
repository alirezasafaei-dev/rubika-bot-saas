from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.filter import Filter, FilterAction


class FilterRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        channel_id: int,
        pattern: str,
        action: FilterAction,
        reason: str | None,
        is_active: bool = True,
    ) -> Filter:
        obj = Filter(
            channel_id=channel_id,
            pattern=pattern,
            action=action,
            reason=reason,
            is_active=is_active,
        )
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def list_by_channel(
        self,
        *,
        channel_id: int,
        page: int,
        limit: int,
        is_active: bool | None = None,
    ) -> tuple[list[Filter], int]:
        conditions = [Filter.channel_id == channel_id]
        if is_active is not None:
            conditions.append(Filter.is_active == is_active)

        total_stmt = select(func.count(Filter.id)).where(*conditions)
        total = int((await self.db.execute(total_stmt)).scalar_one())

        stmt = (
            select(Filter)
            .where(*conditions)
            .order_by(Filter.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    async def list_active_by_channel(self, *, channel_id: int) -> list[Filter]:
        stmt = (
            select(Filter)
            .where(Filter.channel_id == channel_id, Filter.is_active)
            .order_by(Filter.id.asc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_by_id_and_channel(
        self,
        *,
        filter_id: int,
        channel_id: int,
    ) -> Filter | None:
        stmt = select(Filter).where(
            Filter.id == filter_id, Filter.channel_id == channel_id
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def update(
        self,
        *,
        rule: Filter,
        pattern: str | None,
        action: FilterAction | None,
        reason: str | None,
        is_active: bool | None,
    ) -> Filter:
        if pattern is not None:
            rule.pattern = pattern
        if action is not None:
            rule.action = action
        if reason is not None:
            rule.reason = reason
        if is_active is not None:
            rule.is_active = is_active
        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def delete(self, *, rule: Filter) -> None:
        await self.db.delete(rule)
        await self.db.flush()
