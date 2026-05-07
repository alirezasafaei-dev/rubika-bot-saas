"""
Workspace business logic: CRUD, membership management, ownership checks.
"""
from __future__ import annotations

from math import ceil
from typing import List, Optional, Tuple

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceMemberAdd,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceRole,
    WorkspaceStatus,
    WorkspaceUpdate,
)


class WorkspaceRepository(BaseRepository[Workspace]):
    """Data-access layer for Workspace."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Workspace)


class WorkspaceMemberRepository(BaseRepository[WorkspaceMember]):
    """Data-access layer for WorkspaceMember."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, WorkspaceMember)

    async def get_member(self, workspace_id: int, user_id: int) -> Optional[WorkspaceMember]:
        """Return a specific member record."""
        stmt = select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def count_members(self, workspace_id: int) -> int:
        """Return the number of active members in a workspace."""
        stmt = select(func.count(WorkspaceMember.id)).where(
            WorkspaceMember.workspace_id == workspace_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def list_members(
        self, workspace_id: int, skip: int = 0, limit: int = 100
    ) -> Tuple[List[WorkspaceMember], int]:
        """Return (members_list, total_count)."""
        # Total
        total_stmt = select(func.count(WorkspaceMember.id)).where(
            WorkspaceMember.workspace_id == workspace_id,
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar_one()

        # Members with user info
        stmt = (
            select(WorkspaceMember)
            .where(WorkspaceMember.workspace_id == workspace_id)
            .options(joinedload(WorkspaceMember.user))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        members = list(result.unique().scalars().all())

        return members, total


class WorkspaceService:
    """Business logic for workspace management."""

    def __init__(self, db: AsyncSession, current_user: User) -> None:
        self.db = db
        self.user = current_user
        self.ws_repo = WorkspaceRepository(db)
        self.member_repo = WorkspaceMemberRepository(db)

    # ── Authorisation helpers ───────────────────────────────────────

    async def _get_workspace_or_404(self, workspace_id: int) -> Workspace:
        """Return workspace or raise 404."""
        ws = await self.ws_repo.get(workspace_id)
        if not ws or (ws.deleted_at is not None):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "WORKSPACE_NOT_FOUND", "message": "Workspace not found."},
            )
        return ws

    async def _check_member(self, workspace_id: int, user_id: int) -> WorkspaceMember:
        """Return member record or raise 403."""
        member = await self.member_repo.get_member(workspace_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NOT_A_MEMBER",
                    "message": "You are not a member of this workspace.",
                },
            )
        return member

    async def _check_admin_or_owner(self, workspace_id: int, user_id: int) -> WorkspaceMember:
        """Return member record if user is admin/owner, else raise 403."""
        member = await self._check_member(workspace_id, user_id)
        if member.role not in (WorkspaceRole.OWNER, WorkspaceRole.ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_PERMISSIONS",
                    "message": "Admin or Owner role required.",
                },
            )
        return member

    async def _check_owner(self, workspace_id: int) -> Workspace:
        """Verify current user is the workspace owner."""
        ws = await self._get_workspace_or_404(workspace_id)
        if ws.owner_id != self.user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "NOT_OWNER",
                    "message": "Only the workspace owner can perform this action.",
                },
            )
        return ws

    # ── CRUD ─────────────────────────────────────────────────────────

    async def create(self, payload: WorkspaceCreate) -> WorkspaceResponse:
        """Create a new workspace and add creator as OWNER."""
        ws = await self.ws_repo.create(
            name=payload.name.strip(),
            description=payload.description.strip() if payload.description else None,
            owner_id=self.user.id,
            status=WorkspaceStatus.ACTIVE,
        )
        # Add creator as owner
        await self.member_repo.create(
            workspace_id=ws.id,
            user_id=self.user.id,
            role=WorkspaceRole.OWNER,
        )
        return await self._build_response(ws)

    async def get(self, workspace_id: int) -> WorkspaceResponse:
        """Return workspace if current user is a member."""
        ws = await self._get_workspace_or_404(workspace_id)
        await self._check_member(workspace_id, self.user.id)
        return await self._build_response(ws)

    async def list_mine(
        self, page: int = 1, limit: int = 20
    ) -> dict:
        """Return paginated workspaces where current user is a member."""
        # Workspace IDs where user is a member
        member_sub = (
            select(WorkspaceMember.workspace_id)
            .where(WorkspaceMember.user_id == self.user.id)
            .subquery()
        )
        total_stmt = select(func.count(Workspace.id)).where(
            Workspace.id.in_(select(member_sub.c.workspace_id)),
            Workspace.deleted_at.is_(None),
        )
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar_one()

        skip = (page - 1) * limit
        stmt = (
            select(Workspace)
            .where(
                Workspace.id.in_(select(member_sub.c.workspace_id)),
                Workspace.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
            .order_by(Workspace.created_at.desc())
        )
        result = await self.db.execute(stmt)
        workspaces = list(result.scalars().all())

        items = [await self._build_response(ws) for ws in workspaces]
        pages = ceil(total / limit) if total > 0 else 1

        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }

    async def update(self, workspace_id: int, payload: WorkspaceUpdate) -> WorkspaceResponse:
        """Update workspace (owner or admin only)."""
        ws = await self._get_workspace_or_404(workspace_id)
        await self._check_admin_or_owner(workspace_id, self.user.id)

        update_kwargs = payload.model_dump(exclude_unset=True)
        if not update_kwargs:
            return await self._build_response(ws)

        updated = await self.ws_repo.update(workspace_id, **update_kwargs)
        return await self._build_response(updated)  # type: ignore[arg-type]

    async def delete(self, workspace_id: int) -> None:
        """Soft-delete a workspace (owner only)."""
        await self._check_owner(workspace_id)
        await self.ws_repo.soft_delete(workspace_id)

    # ── Members ──────────────────────────────────────────────────────

    async def add_member(
        self, workspace_id: int, payload: WorkspaceMemberAdd
    ) -> WorkspaceMemberResponse:
        """Add a user to the workspace (admin/owner only)."""
        ws = await self._get_workspace_or_404(workspace_id)
        await self._check_admin_or_owner(workspace_id, self.user.id)

        # Verify target user exists
        from app.repositories.user_repository import UserRepository
        user_repo = UserRepository(self.db)
        target_user = await user_repo.get(payload.user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "USER_NOT_FOUND", "message": "User not found."},
            )

        # Check not already a member
        existing = await self.member_repo.get_member(workspace_id, payload.user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "ALREADY_MEMBER",
                    "message": "User is already a member of this workspace.",
                },
            )

        member = await self.member_repo.create(
            workspace_id=workspace_id,
            user_id=payload.user_id,
            role=payload.role,
        )

        return await self._build_member_response(member, target_user)

    async def list_members(
        self, workspace_id: int, page: int = 1, limit: int = 20
    ) -> dict:
        """Return paginated members of a workspace."""
        ws = await self._get_workspace_or_404(workspace_id)
        await self._check_member(workspace_id, self.user.id)

        skip = (page - 1) * limit
        members, total = await self.member_repo.list_members(workspace_id, skip, limit)

        items = []
        for m in members:
            items.append(await self._build_member_response(m, m.user))

        pages = ceil(total / limit) if total > 0 else 1
        return {
            "items": items,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": pages,
        }

    async def remove_member(self, workspace_id: int, user_id: int) -> None:
        """Remove a member from the workspace (admin/owner or self)."""
        ws = await self._get_workspace_or_404(workspace_id)

        # Owner can't be removed
        if ws.owner_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "CANNOT_REMOVE_OWNER",
                    "message": "Cannot remove the workspace owner.",
                },
            )

        # Only admin/owner or the user themselves can remove
        if user_id != self.user.id:
            await self._check_admin_or_owner(workspace_id, self.user.id)

        member = await self.member_repo.get_member(workspace_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "MEMBER_NOT_FOUND",
                    "message": "Member not found in this workspace.",
                },
            )

        await self.member_repo.hard_delete(member.id)

    # ── Response builders ────────────────────────────────────────────

    async def _build_response(self, ws: Workspace) -> WorkspaceResponse:
        """Construct a WorkspaceResponse with member count."""
        count = await self.member_repo.count_members(ws.id)
        return WorkspaceResponse(
            id=ws.id,
            name=ws.name,
            description=ws.description,
            owner_id=ws.owner_id,
            status=ws.status,
            member_count=count,
            created_at=ws.created_at,
            updated_at=ws.updated_at,
        )

    async def _build_member_response(
        self, member: WorkspaceMember, user: User
    ) -> WorkspaceMemberResponse:
        """Construct a WorkspaceMemberResponse."""
        return WorkspaceMemberResponse(
            id=member.id,
            user_id=member.user_id,
            full_name=user.full_name,
            username=user.username,
            phone=user.phone,
            role=member.role,
            joined_at=member.created_at,
        )


# ── FastAPI dependency ──────────────────────────────────────────────

async def get_workspace_service(
    db: AsyncSession = Depends(get_db),
    credentials: str = Depends(lambda: None),  # Will be overridden in endpoints
) -> WorkspaceService:
    """Placeholder – real auth wiring happens in the endpoint layer."""
    raise NotImplementedError("Use get_workspace_service_for_user instead")


async def get_workspace_service_for_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(lambda: None),
) -> WorkspaceService:
    """Provide a WorkspaceService with an authenticated user.

    This is called from the endpoint layer after token extraction.
    """
    from app.services.auth_service import AuthService
    auth = AuthService(db)
    user = await auth.get_current_user(token)
    return WorkspaceService(db, user)
