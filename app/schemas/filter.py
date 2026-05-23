from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.filter import FilterAction, FilterMatchType


class FilterCreate(BaseModel):
    pattern: str = Field(..., min_length=1, max_length=500)
    match_type: FilterMatchType = FilterMatchType.CONTAINS
    action: FilterAction
    reason: str | None = Field(default=None, min_length=1, max_length=500)
    is_active: bool = True


class FilterUpdate(BaseModel):
    pattern: str | None = Field(default=None, min_length=1, max_length=500)
    match_type: FilterMatchType | None = None
    action: FilterAction | None = None
    reason: str | None = Field(default=None, min_length=1, max_length=500)
    is_active: bool | None = None


class FilterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: int
    pattern: str
    match_type: FilterMatchType
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
    active_count: int
