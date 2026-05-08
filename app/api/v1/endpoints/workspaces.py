# app/api/v1/endpoints/workspaces.py
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceMemberAdd,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.auth_service import AuthService
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])
security_scheme = HTTPBearer(auto_error=False)


async def _get_workspace_service(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceService:
    """Resolve current user from bearer token and return authenticated workspace service."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authorization header required."},
        )

    auth = AuthService(db)
    user = await auth.get_current_user(credentials.credentials)
    return WorkspaceService(db, user)


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceResponse:
    return await service.create(payload)


@router.get("", response_model=dict)
async def list_workspaces(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    service: WorkspaceService = Depends(_get_workspace_service),
) -> dict:
    return await service.list_mine(page=page, limit=limit)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceResponse:
    return await service.get(workspace_id)


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    payload: WorkspaceUpdate,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceResponse:
    return await service.update(workspace_id, payload)


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: int,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> None:
    await service.delete(workspace_id)


@router.post(
    "/{workspace_id}/members",
    response_model=WorkspaceMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_member(
    workspace_id: int,
    payload: WorkspaceMemberAdd,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceMemberResponse:
    return await service.add_member(workspace_id, payload)


@router.get("/{workspace_id}/members", response_model=dict)
async def list_members(
    workspace_id: int,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    service: WorkspaceService = Depends(_get_workspace_service),
) -> dict:
    return await service.list_members(workspace_id, page=page, limit=limit)


@router.delete("/{workspace_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(
    workspace_id: int,
    user_id: int,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> None:
    await service.remove_member(workspace_id, user_id)
