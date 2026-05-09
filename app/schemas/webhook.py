from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RubikaWebhookPayload(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=50)
    message: str | None = Field(default=None, max_length=2000)
    sender_rubika_user_id: str | None = Field(default=None, max_length=64)
    message_id: str | None = Field(default=None, max_length=128)
    sent_at: datetime | None = None


class RubikaWebhookResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    accepted: bool
    reason: str
