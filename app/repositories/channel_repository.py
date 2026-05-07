from __future__ import annotations

from app.models.channel import Channel
from app.repositories.base import BaseRepository


class ChannelRepository(BaseRepository[Channel]):
    """Channel-specific repository methods."""

    model = Channel
