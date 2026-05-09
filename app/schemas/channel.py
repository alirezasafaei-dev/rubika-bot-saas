from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChannelCreate(BaseModel):
    """Create a new channel."""

    model_config = ConfigDict(from_attributes=True)

    rubika_channel_id: str = Field(..., min_length=1, max_length=255)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)


class ChannelUpdate(BaseModel):
    """Update channel fields (all optional)."""

    model_config = ConfigDict(from_attributes=True)

    rubika_channel_id: str | None = Field(
        None,
        min_length=1,
        max_length=255,
    )
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    is_active: bool | None = None


class ChannelResponse(BaseModel):
    """Channel response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    workspace_id: int
    rubika_channel_id: str
    name: str
    description: str | None = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class ChannelListResponse(BaseModel):
    """Paginated list of channels."""

    items: list[ChannelResponse]
    total: int
    page: int
    limit: int
    pages: int
