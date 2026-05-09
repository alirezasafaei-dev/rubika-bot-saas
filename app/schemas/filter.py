from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.filter import FilterAction


class FilterCreate(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=500)
    action: FilterAction
    reason: str | None = Field(default=None, min_length=1, max_length=500)
    is_active: bool = True


class FilterUpdate(BaseModel):
    pattern: str | None = Field(default=None, min_length=1, max_length=500)
    action: FilterAction | None = None
    reason: str | None = Field(default=None, min_length=1, max_length=500)
    is_active: bool | None = None


class FilterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: int
    pattern: str
    action: FilterAction
    reason: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class FilterListResponse(BaseModel):
    items: list[FilterResponse]
    page: int
    limit: int
    total: int
