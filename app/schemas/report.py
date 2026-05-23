from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class ReportSummaryItem(BaseModel):
    created_posts: int
    scheduled_posts: int
    sent_posts: int
    failed_posts: int
    auto_replies_sent: int
    deleted_messages: int
    webhook_delivery_results: int
    webhook_processing_errors: int


class ReportSummaryResponse(BaseModel):
    workspace_id: int
    channel_id: int | None = None
    from_date: str | None = None
    to_date: str | None = None
    summary: ReportSummaryItem


class DailyReportItem(BaseModel):
    date: date
    sent_posts: int
    failed_posts: int
    auto_replies_sent: int
    deleted_messages: int
    webhook_processing_errors: int


class DailyReportResponse(BaseModel):
    workspace_id: int
    from_date: str | None = None
    to_date: str | None = None
    items: list[DailyReportItem]
