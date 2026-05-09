from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_auto_reply_service, get_current_user
from app.models.user import User
from app.schemas.auto_reply import (
    AutoReplyCreate,
    AutoReplyListResponse,
    AutoReplyLogsResponse,
    AutoReplyResponse,
    AutoReplyToggle,
    AutoReplyUpdate,
)
from app.services.auto_reply_service import AutoReplyService

router = APIRouter(tags=["auto-replies"])


@router.post(
    "/workspaces/{workspace_id}/channels/{channel_id}/auto-replies",
    response_model=AutoReplyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_auto_reply(
    workspace_id: int,
    channel_id: int,
    payload: AutoReplyCreate,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AutoReplyService, Depends(get_auto_reply_service)],
) -> AutoReplyResponse:
    del _current_user
    rule = await service.create_reply(
        workspace_id=workspace_id,
        channel_id=channel_id,
        trigger_text=payload.trigger_text.strip(),
        reply_text=payload.reply_text.strip(),
        is_active=payload.is_active,
    )
    return AutoReplyResponse.model_validate(rule)


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/auto-replies",
    response_model=AutoReplyListResponse,
)
async def list_auto_replies(
    workspace_id: int,
    channel_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AutoReplyService, Depends(get_auto_reply_service)],
    is_active: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> AutoReplyListResponse:
    del _current_user
    items, total = await service.list_replies(
        workspace_id=workspace_id,
        channel_id=channel_id,
        page=page,
        limit=limit,
        is_active=is_active,
    )
    return AutoReplyListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/logs",
    response_model=AutoReplyLogsResponse,
)
async def get_auto_reply_logs(
    workspace_id: int,
    channel_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AutoReplyService, Depends(get_auto_reply_service)],
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> AutoReplyLogsResponse:
    del _current_user
    items, total = await service.get_logs(
        workspace_id=workspace_id,
        channel_id=channel_id,
        page=page,
        limit=limit,
    )
    response_items = [
        {
            "rule_id": item["rule_id"],
            "event": item["event"],
            "created_at": item["created_at"],
        }
        for item in items
    ]
    return AutoReplyLogsResponse(
        items=response_items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}",
    response_model=AutoReplyResponse,
)
async def get_auto_reply(
    workspace_id: int,
    channel_id: int,
    rule_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AutoReplyService, Depends(get_auto_reply_service)],
) -> AutoReplyResponse:
    del _current_user
    rule = await service.get_reply(
        workspace_id=workspace_id,
        channel_id=channel_id,
        rule_id=rule_id,
    )
    return AutoReplyResponse.model_validate(rule)


@router.patch(
    "/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}",
    response_model=AutoReplyResponse,
)
async def update_auto_reply(
    workspace_id: int,
    channel_id: int,
    rule_id: int,
    payload: AutoReplyUpdate,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AutoReplyService, Depends(get_auto_reply_service)],
) -> AutoReplyResponse:
    del _current_user
    rule = await service.update_reply(
        workspace_id=workspace_id,
        channel_id=channel_id,
        rule_id=rule_id,
        trigger_text=(payload.trigger_text.strip() if payload.trigger_text else None),
        reply_text=(payload.reply_text.strip() if payload.reply_text else None),
        is_active=payload.is_active,
    )
    return AutoReplyResponse.model_validate(rule)


@router.post(
    "/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}/toggle",
    response_model=AutoReplyResponse,
)
async def toggle_auto_reply(
    workspace_id: int,
    channel_id: int,
    rule_id: int,
    payload: AutoReplyToggle,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AutoReplyService, Depends(get_auto_reply_service)],
) -> AutoReplyResponse:
    del _current_user
    rule = await service.toggle_reply(
        workspace_id=workspace_id,
        channel_id=channel_id,
        rule_id=rule_id,
        is_active=payload.is_active,
    )
    return AutoReplyResponse.model_validate(rule)


@router.delete(
    "/workspaces/{workspace_id}/channels/{channel_id}/auto-replies/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_auto_reply(
    workspace_id: int,
    channel_id: int,
    rule_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[AutoReplyService, Depends(get_auto_reply_service)],
) -> Response:
    del _current_user
    await service.delete_reply(
        workspace_id=workspace_id,
        channel_id=channel_id,
        rule_id=rule_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
