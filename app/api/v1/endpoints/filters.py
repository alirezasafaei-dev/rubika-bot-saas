from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import get_current_user, get_filter_service
from app.models.user import User
from app.schemas.filter import (
    FilterCreate,
    FilterListResponse,
    FilterResponse,
    FilterUpdate,
)
from app.services.filter_service import FilterService

router = APIRouter(tags=["filters"])


@router.post(
    "/workspaces/{workspace_id}/channels/{channel_id}/filters",
    response_model=FilterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_filter(
    workspace_id: int,
    channel_id: int,
    payload: FilterCreate,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[FilterService, Depends(get_filter_service)],
) -> FilterResponse:
    del _current_user
    rule = await service.create_filter(
        workspace_id=workspace_id,
        channel_id=channel_id,
        pattern=payload.pattern.strip(),
        action=payload.action,
        reason=payload.reason,
        is_active=payload.is_active,
    )
    return FilterResponse.model_validate(rule)


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/filters",
    response_model=FilterListResponse,
)
async def list_filters(
    workspace_id: int,
    channel_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[FilterService, Depends(get_filter_service)],
    is_active: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> FilterListResponse:
    del _current_user
    items, total = await service.list_filters(
        workspace_id=workspace_id,
        channel_id=channel_id,
        page=page,
        limit=limit,
        is_active=is_active,
    )
    return FilterListResponse(
        items=items,
        page=page,
        limit=limit,
        total=total,
    )


@router.get(
    "/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}",
    response_model=FilterResponse,
)
async def get_filter(
    workspace_id: int,
    channel_id: int,
    rule_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[FilterService, Depends(get_filter_service)],
) -> FilterResponse:
    del _current_user
    rule = await service.get_filter(
        workspace_id=workspace_id,
        channel_id=channel_id,
        rule_id=rule_id,
    )
    return FilterResponse.model_validate(rule)


@router.patch(
    "/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}",
    response_model=FilterResponse,
)
async def update_filter(
    workspace_id: int,
    channel_id: int,
    rule_id: int,
    payload: FilterUpdate,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[FilterService, Depends(get_filter_service)],
) -> FilterResponse:
    del _current_user
    rule = await service.update_filter(
        workspace_id=workspace_id,
        channel_id=channel_id,
        rule_id=rule_id,
        pattern=(payload.pattern.strip() if payload.pattern else None),
        action=payload.action,
        reason=payload.reason,
        is_active=payload.is_active,
    )
    return FilterResponse.model_validate(rule)


@router.delete(
    "/workspaces/{workspace_id}/channels/{channel_id}/filters/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_filter(
    workspace_id: int,
    channel_id: int,
    rule_id: int,
    _current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[FilterService, Depends(get_filter_service)],
) -> Response:
    del _current_user
    await service.delete_filter(
        workspace_id=workspace_id,
        channel_id=channel_id,
        rule_id=rule_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
