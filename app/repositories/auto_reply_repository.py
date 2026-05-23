from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auto_reply import AutoReply


class AutoReplyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        *,
        channel_id: int,
        trigger_text: str,
        match_type,
        reply_text: str,
        rich_reply_json: str | None,
        next_step_id: int | None,
        is_active: bool = True,
    ) -> AutoReply:
        obj = AutoReply(
            channel_id=channel_id,
            trigger_text=trigger_text,
            match_type=match_type,
            reply_text=reply_text,
            rich_reply_json=rich_reply_json,
            next_step_id=next_step_id,
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
        query: str | None = None,
    ) -> tuple[list[AutoReply], int]:
        conditions = [AutoReply.channel_id == channel_id]
        if is_active is not None:
            conditions.append(AutoReply.is_active == is_active)
        if query:
            search = f"%{query}%"
            conditions.append(
                or_(
                    AutoReply.trigger_text.ilike(search),
                    AutoReply.reply_text.ilike(search),
                )
            )

        count_stmt = select(func.count(AutoReply.id)).where(*conditions)
        total = int((await self.db.execute(count_stmt)).scalar_one())

        stmt = (
            select(AutoReply)
            .where(*conditions)
            .order_by(AutoReply.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        items = list((await self.db.execute(stmt)).scalars().all())
        return items, total

    async def count_active_by_channel(self, *, channel_id: int) -> int:
        stmt = select(func.count(AutoReply.id)).where(
            AutoReply.channel_id == channel_id,
            AutoReply.is_active,
        )
        return int((await self.db.execute(stmt)).scalar_one())

    async def list_active_by_channel(self, *, channel_id: int) -> list[AutoReply]:
        stmt = (
            select(AutoReply)
            .where(AutoReply.channel_id == channel_id, AutoReply.is_active)
            .order_by(AutoReply.id.asc())
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_by_id_and_channel(
        self,
        *,
        rule_id: int,
        channel_id: int,
    ) -> AutoReply | None:
        stmt = select(AutoReply).where(
            AutoReply.id == rule_id,
            AutoReply.channel_id == channel_id,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def update(
        self,
        *,
        rule: AutoReply,
        trigger_text: str | None,
        match_type,
        reply_text: str | None,
        rich_reply_json: str | None,
        next_step_id: int | None,
        is_active: bool | None,
    ) -> AutoReply:
        if trigger_text is not None:
            rule.trigger_text = trigger_text
        if match_type is not None:
            rule.match_type = match_type
        if reply_text is not None:
            rule.reply_text = reply_text
        if rich_reply_json is not None:
            rule.rich_reply_json = rich_reply_json
        rule.next_step_id = next_step_id
        if is_active is not None:
            rule.is_active = is_active

        await self.db.flush()
        await self.db.refresh(rule)
        return rule

    async def delete(self, *, rule: AutoReply) -> None:
        await self.db.delete(rule)
        await self.db.flush()
