"""
Workspace schemas: create, update, response, member management.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class WorkspaceStatus(str, enum.Enum):
    """Workspace status values."""
    ACTIVE = "active"
    DISABLED = "disabled"
    DELETED = "deleted"


class WorkspaceRole(str, enum.Enum):
    """Member role within a workspace."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


# ── Request Schemas ─────────────────────────────────────────────────

class WorkspaceCreate(BaseModel):
    """Create a new workspace."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)


class WorkspaceUpdate(BaseModel):
    """Update workspace fields (all optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[WorkspaceStatus] = None


class WorkspaceMemberAdd(BaseModel):
    """Add an existing user to a workspace."""
    user_id: int = Field(..., gt=0)
    role: WorkspaceRole = WorkspaceRole.MEMBER


# ── Response Schemas ────────────────────────────────────────────────

class WorkspaceMemberResponse(BaseModel):
    """Public info about a workspace member."""
    id: int
    user_id: int
    full_name: str
    username: Optional[str] = None
    phone: str
    role: WorkspaceRole
    joined_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceResponse(BaseModel):
    """Public workspace info."""
    id: int
    name: str
    description: Optional[str] = None
    owner_id: int
    status: WorkspaceStatus = WorkspaceStatus.ACTIVE
    member_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class WorkspaceListResponse(BaseModel):
    """Paginated list of workspaces."""
    items: List[WorkspaceResponse]
    total: int
    page: int
    limit: int
    pages: int
