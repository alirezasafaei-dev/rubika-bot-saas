from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RubikaWebhookPayload(BaseModel):
    event_type: Literal["message_received", "delivery_result"] = Field(
        ..., description="Webhook event type"
    )
    message: str | None = Field(default=None, max_length=2000)
    sender_rubika_user_id: str | None = Field(default=None, max_length=64)
    message_id: str | None = Field(default=None, max_length=128)
    sent_at: datetime | None = None


class RubikaWebhookResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    accepted: bool
    reason: str


class RubikaWebhookAdapterPayload(BaseModel):
    """Raw Rubika webhook payload (or canonical format)."""

    model_config = ConfigDict(extra="allow")

    event_type: str | None = Field(default=None)
    message: str | None = Field(default=None, max_length=2000)
    sender_rubika_user_id: str | None = Field(default=None, max_length=64)
    message_id: str | None = Field(default=None, max_length=128)
    rubika_channel_id: str | None = Field(default=None, max_length=255)
