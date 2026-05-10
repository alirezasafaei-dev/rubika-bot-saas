from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ScheduledPostStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduledPostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=4000)
    scheduled_at: datetime

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("content must not be empty")
        return value

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, value: datetime) -> datetime:
        if value <= datetime.now(UTC):
            raise ValueError("scheduled_at must be in the future")
        return value


class ScheduledPostUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=4000)
    scheduled_at: datetime | None = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("content must not be empty")
        return value

    @field_validator("scheduled_at")
    @classmethod
    def validate_scheduled_at(cls, value: datetime | None) -> datetime | None:
        if value is None:
            return value
        if value <= datetime.now(UTC):
            raise ValueError("scheduled_at must be in the future")
        return value


class ScheduledPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    channel_id: int
    content: str
    scheduled_at: datetime
    status: ScheduledPostStatus
    sent_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class ScheduledPostListResponse(BaseModel):
    items: list[ScheduledPostResponse]
    page: int
    limit: int
    total: int


class ScheduledPostLogItem(BaseModel):
    status: ScheduledPostStatus
    error_message: str | None
    sent_at: datetime | None
    updated_at: datetime


class ScheduledPostLogsResponse(BaseModel):
    items: list[ScheduledPostLogItem]
