from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_current_user, get_report_service
from app.models.user import User
from app.schemas.report import (
    DailyReportResponse,
    ReportSummaryResponse,
)
from app.services.report_service import ReportService

router = APIRouter(tags=["reports"])


@router.get(
    "/workspaces/{workspace_id}/reports/summary",
    response_model=ReportSummaryResponse,
)
async def workspace_summary(
    workspace_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
) -> ReportSummaryResponse:
    user_id = _current_user.id
    try:
        result = await service.get_workspace_summary(
            workspace_id=workspace_id,
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return ReportSummaryResponse(
        workspace_id=workspace_id,
        from_date=from_date,
        to_date=to_date,
        summary=result,
    )


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/reports/summary",
    response_model=ReportSummaryResponse,
)
async def channel_summary(
    workspace_id: int,
    channel_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
) -> ReportSummaryResponse:
    user_id = _current_user.id
    try:
        result = await service.get_channel_summary(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return ReportSummaryResponse(
        workspace_id=workspace_id,
        channel_id=channel_id,
        from_date=from_date,
        to_date=to_date,
        summary=result,
    )


@router.get(
    "/workspaces/{workspace_id}/reports/daily",
    response_model=DailyReportResponse,
)
async def daily_report(
    workspace_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[ReportService, Depends(get_report_service)],
    days: int = Query(default=7, ge=1, le=90),
) -> DailyReportResponse:
    user_id = _current_user.id
    try:
        items = await service.get_daily(
            workspace_id=workspace_id,
            user_id=user_id,
            days=days,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return DailyReportResponse(
        workspace_id=workspace_id,
        items=items,
    )
