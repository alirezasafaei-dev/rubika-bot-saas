from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.repositories.base import BaseRepository


class ChannelRepository(BaseRepository[Channel]):
    """Channel-specific repository methods."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Channel, session)

    async def get_by_rubika_channel_id(
        self, rubika_channel_id: str
    ) -> Channel | None:
        return await self.get_one_by(rubika_channel_id=rubika_channel_id)
