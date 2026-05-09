from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.repositories.base import BaseRepository


class ChannelRepository(BaseRepository[Channel]):
    """Channel-specific repository methods."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Channel, session)
