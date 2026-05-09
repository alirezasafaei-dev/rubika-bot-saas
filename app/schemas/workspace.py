from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, Field


class WorkspaceStatus(enum.StrEnum):
    """Workspace status values."""

    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"


class WorkspaceRole(enum.StrEnum):
    """Member role within a workspace."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceCreate(BaseModel):
    """Create a new workspace."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)


class WorkspaceUpdate(BaseModel):
    """Update workspace fields (all optional)."""

    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    status: WorkspaceStatus | None = None


class WorkspaceMemberAdd(BaseModel):
    """Add an existing user to a workspace."""

    user_id: int = Field(..., gt=0)
    role: WorkspaceRole = WorkspaceRole.MEMBER


class WorkspaceMemberResponse(BaseModel):
    """Public info about a workspace member."""

    id: int
    user_id: int
    workspace_id: int
    role: WorkspaceRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceResponse(BaseModel):
    """Public workspace info."""

    id: int
    name: str
    description: str | None = None
    owner_id: int
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    member_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class WorkspaceListResponse(BaseModel):
    """Paginated list of workspaces."""

    items: list[WorkspaceResponse]
    total: int
    page: int
    limit: int
    pages: int


class WorkspaceMemberCreate(BaseModel):
    """Internal schema for creating workspace member."""

    user_id: int = Field(..., gt=0)
    role: WorkspaceRole = WorkspaceRole.MEMBER
