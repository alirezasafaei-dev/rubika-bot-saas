from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AutoReplyToggle(BaseModel):
    is_active: bool


class AutoReplyCreate(BaseModel):
    trigger_text: str = Field(..., min_length=1, max_length=500)
    reply_text: str = Field(..., min_length=1)
    is_active: bool = True


class AutoReplyUpdate(BaseModel):
    trigger_text: str | None = Field(default=None, min_length=1, max_length=500)
    reply_text: str | None = Field(default=None, min_length=1)
    is_active: bool | None = None


class AutoReplyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: int
    trigger_text: str
    reply_text: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AutoReplyListResponse(BaseModel):
    items: list[AutoReplyResponse]
    page: int
    limit: int
    total: int


class AutoReplyLogItem(BaseModel):
    rule_id: int
    event: str
    created_at: datetime


class AutoReplyLogsResponse(BaseModel):
    items: list[AutoReplyLogItem]
    page: int
    limit: int
    total: int
