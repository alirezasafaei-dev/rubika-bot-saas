"""
Workspace API endpoints: CRUD + membership management.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceMemberAdd,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.services.auth_service import AuthService, get_auth_service
from app.services.workspace_service import WorkspaceService
from app.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/workspaces", tags=["workspaces"])
security_scheme = HTTPBearer(auto_error=False)


async def _get_workspace_service(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> WorkspaceService:
    """Extract token, resolve user, and return an authenticated WorkspaceService."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authorization header required."},
        )
    auth = AuthService(db)
    user = await auth.get_current_user(credentials.credentials)
    return WorkspaceService(db, user)


# ── CRUD ────────────────────────────────────────────────────────────

@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    payload: WorkspaceCreate,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceResponse:
    """Create a new workspace (authenticated user becomes owner)."""
    return await service.create(payload)


@router.get("", response_model=dict)
async def list_workspaces(
    page: int = 1,
    limit: int = 20,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> dict:
    """List workspaces where the current user is a member."""
    return await service.list_mine(page=page, limit=limit)


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: int,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceResponse:
    """Get a single workspace by ID (must be a member)."""
    return await service.get(workspace_id)


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
async def update_workspace(
    workspace_id: int,
    payload: WorkspaceUpdate,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceResponse:
    """Update workspace fields (admin/owner only)."""
    return await service.update(workspace_id, payload)


@router.delete("/{workspace_id}", status_code=204)
async def delete_workspace(
    workspace_id: int,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> None:
    """Soft-delete a workspace (owner only)."""
    await service.delete(workspace_id)


# ── Members ─────────────────────────────────────────────────────────

@router.post("/{workspace_id}/members", response_model=WorkspaceMemberResponse, status_code=201)
async def add_member(
    workspace_id: int,
    payload: WorkspaceMemberAdd,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> WorkspaceMemberResponse:
    """Add a user to the workspace (admin/owner only)."""
    return await service.add_member(workspace_id, payload)


@router.get("/{workspace_id}/members", response_model=dict)
async def list_members(
    workspace_id: int,
    page: int = 1,
    limit: int = 20,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> dict:
    """List workspace members (any member can view)."""
    return await service.list_members(workspace_id, page=page, limit=limit)


@router.delete("/{workspace_id}/members/{user_id}", status_code=204)
async def remove_member(
    workspace_id: int,
    user_id: int,
    service: WorkspaceService = Depends(_get_workspace_service),
) -> None:
    """Remove a member (admin/owner or self)."""
    await service.remove_member(workspace_id, user_id)
