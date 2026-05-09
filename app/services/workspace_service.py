from __future__ import annotations

from sqlalchemy import func, select

from app.core.errors import AppException, ErrorCode
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceMemberAdd,
    WorkspaceUpdate,
)


class WorkspaceService:
    def __init__(
        self,
        workspace_repository: BaseRepository[Workspace],
        member_repository: BaseRepository[WorkspaceMember],
    ) -> None:
        self.workspace_repository = workspace_repository
        self.member_repository = member_repository

    async def create_workspace(
        self, *, owner_user_id: int, payload: WorkspaceCreate
    ) -> Workspace:
        workspace = await self.workspace_repository.create(
            name=payload.name,
            description=payload.description,
            owner_id=owner_user_id,
        )
        await self.member_repository.create(
            workspace_id=workspace.id,
            user_id=owner_user_id,
            role="owner",
        )
        return workspace

    async def list_workspaces_for_user(
        self,
        *,
        user_id: int,
        page: int,
        limit: int,
    ) -> tuple[list[Workspace], int]:
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.deleted_at.is_(None),
                Workspace.deleted_at.is_(None),
            )
            .order_by(Workspace.id.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await self.workspace_repository.session.execute(stmt)
        items = list(result.scalars().all())

        count_stmt = (
            select(func.count(Workspace.id))
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.deleted_at.is_(None),
                Workspace.deleted_at.is_(None),
            )
        )
        count_result = await self.workspace_repository.session.execute(count_stmt)
        total = count_result.scalar_one()

        return items, total

    async def get_workspace_for_user(
        self, *, workspace_id: int, user_id: int
    ) -> Workspace:
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(
                Workspace.id == workspace_id,
                WorkspaceMember.user_id == user_id,
                WorkspaceMember.deleted_at.is_(None),
                Workspace.deleted_at.is_(None),
            )
        )
        result = await self.workspace_repository.session.execute(stmt)
        workspace = result.scalar_one_or_none()
        if workspace is None:
            raise AppException(ErrorCode.NOT_FOUND, "Workspace not found")
        return workspace

    async def update_workspace(
        self,
        *,
        workspace_id: int,
        user_id: int,
        payload: WorkspaceUpdate,
    ) -> Workspace:
        workspace = await self.get_workspace_for_user(
            workspace_id=workspace_id, user_id=user_id
        )
        if workspace.owner_id != user_id:
            raise AppException(
                ErrorCode.FORBIDDEN, "Only workspace owner can update workspace"
            )
        data = payload.model_dump(exclude_unset=True)
        return await self.workspace_repository.update(workspace, **data)

    async def delete_workspace(self, *, workspace_id: int, user_id: int) -> None:
        workspace = await self.get_workspace_for_user(
            workspace_id=workspace_id, user_id=user_id
        )
        if workspace.owner_id != user_id:
            raise AppException(
                ErrorCode.FORBIDDEN, "Only workspace owner can delete workspace"
            )
        await self.workspace_repository.soft_delete(workspace)

    async def add_member(
        self,
        *,
        workspace_id: int,
        actor_user_id: int,
        payload: WorkspaceMemberAdd,
    ) -> WorkspaceMember:
        workspace = await self.get_workspace_for_user(
            workspace_id=workspace_id, user_id=actor_user_id
        )
        if workspace.owner_id != actor_user_id:
            raise AppException(
                ErrorCode.FORBIDDEN, "Only workspace owner can add members"
            )

        existing = await self.member_repository.get_one_by(
            workspace_id=workspace_id,
            user_id=payload.user_id,
        )
        if existing is not None:
            raise AppException(ErrorCode.CONFLICT, "Member already exists")

        return await self.member_repository.create(
            workspace_id=workspace_id,
            user_id=payload.user_id,
            role=payload.role,
        )

    async def remove_member(
        self,
        *,
        workspace_id: int,
        actor_user_id: int,
        member_user_id: int,
    ) -> None:
        workspace = await self.get_workspace_for_user(
            workspace_id=workspace_id, user_id=actor_user_id
        )
        if workspace.owner_id != actor_user_id:
            raise AppException(
                ErrorCode.FORBIDDEN, "Only workspace owner can remove members"
            )

        member = await self.member_repository.get_one_by(
            workspace_id=workspace_id,
            user_id=member_user_id,
        )
        if member is None:
            raise AppException(ErrorCode.NOT_FOUND, "Member not found")

        await self.member_repository.soft_delete(member)

    async def list_members(
        self,
        *,
        workspace_id: int,
        user_id: int,
    ) -> list[WorkspaceMember]:
        await self.get_workspace_for_user(workspace_id=workspace_id, user_id=user_id)

        stmt = (
            select(WorkspaceMember)
            .where(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.deleted_at.is_(None),
            )
            .order_by(WorkspaceMember.id.asc())
        )
        result = await self.member_repository.session.execute(stmt)
        return list(result.scalars().all())

    async def list_workspaces(
        self,
        *,
        user_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Workspace], int]:
        return await self.list_workspaces_for_user(
            user_id=user_id,
            page=page,
            limit=limit,
        )

    async def get_workspace(
        self,
        *,
        workspace_id: int,
        user_id: int,
    ) -> Workspace:
        return await self.get_workspace_for_user(
            workspace_id=workspace_id,
            user_id=user_id,
        )
