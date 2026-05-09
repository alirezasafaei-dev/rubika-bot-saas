from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.errors import AppException, ErrorCode, NotFoundError
from app.models.scheduled_post import PostStatus, ScheduledPost
from app.repositories.channel_repository import ChannelRepository
from app.repositories.scheduled_post_repository import ScheduledPostRepository
from app.schemas.scheduled_post import (
    ScheduledPostCreate,
    ScheduledPostListResponse,
    ScheduledPostLogItem,
    ScheduledPostLogsResponse,
    ScheduledPostUpdate,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.user import User


class ScheduledPostService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repository = ScheduledPostRepository(db)
        self.channel_repo = ChannelRepository(db)

    async def _get_workspace_channel(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        user_id: int,
    ):
        del user_id
        channel = await self.channel_repo.get_by_id(channel_id)
        if channel is None or channel.workspace_id != workspace_id:
            raise NotFoundError(
                error_code=ErrorCode.CHANNEL_NOT_FOUND,
                message="Channel not found",
            )
        return channel

    async def _get_post_or_404(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        post_id: int,
        user_id: int,
    ) -> ScheduledPost:
        await self._get_workspace_channel(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=user_id,
        )

        post = await self.repository.get_by_id_and_channel(
            post_id=post_id,
            channel_id=channel_id,
        )
        if post is None:
            raise NotFoundError(
                error_code=ErrorCode.SCHEDULED_POST_NOT_FOUND,
                message="Scheduled post not found",
            )
        return post

    async def create_post(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        payload: ScheduledPostCreate,
        current_user: User,
    ) -> ScheduledPost:
        await self._get_workspace_channel(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=current_user.id,
        )

        post = await self.repository.create(
            channel_id=channel_id,
            content=payload.content,
            scheduled_at=payload.scheduled_at,
        )
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def list_posts(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        page: int,
        limit: int,
        current_user: User,
    ) -> ScheduledPostListResponse:
        await self._get_workspace_channel(
            workspace_id=workspace_id,
            channel_id=channel_id,
            user_id=current_user.id,
        )

        items, total = await self.repository.list_by_channel(
            channel_id=channel_id,
            page=page,
            limit=limit,
        )
        return ScheduledPostListResponse(
            items=items,
            total=total,
            page=page,
            limit=limit,
        )

    async def get_post(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        post_id: int,
        current_user: User,
    ) -> ScheduledPost:
        return await self._get_post_or_404(
            workspace_id=workspace_id,
            channel_id=channel_id,
            post_id=post_id,
            user_id=current_user.id,
        )

    async def update_post(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        post_id: int,
        payload: ScheduledPostUpdate,
        current_user: User,
    ) -> ScheduledPost:
        post = await self._get_post_or_404(
            workspace_id=workspace_id,
            channel_id=channel_id,
            post_id=post_id,
            user_id=current_user.id,
        )

        if post.status != PostStatus.PENDING:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="Only pending posts can be updated",
            )

        post = await self.repository.update_pending_post(
            post=post,
            content=payload.content,
            scheduled_at=payload.scheduled_at,
        )
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def cancel_post(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        post_id: int,
        current_user: User,
    ) -> ScheduledPost:
        post = await self._get_post_or_404(
            workspace_id=workspace_id,
            channel_id=channel_id,
            post_id=post_id,
            user_id=current_user.id,
        )

        if post.status != PostStatus.PENDING:
            raise AppException(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="Only pending posts can be cancelled",
            )

        post = await self.repository.cancel(post=post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete_post(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        post_id: int,
        current_user: User,
    ) -> None:
        post = await self._get_post_or_404(
            workspace_id=workspace_id,
            channel_id=channel_id,
            post_id=post_id,
            user_id=current_user.id,
        )
        await self.repository.delete(post=post)
        await self.db.commit()

    async def get_logs(
        self,
        *,
        workspace_id: int,
        channel_id: int,
        post_id: int,
        current_user: User,
    ) -> ScheduledPostLogsResponse:
        post = await self._get_post_or_404(
            workspace_id=workspace_id,
            channel_id=channel_id,
            post_id=post_id,
            user_id=current_user.id,
        )
        return ScheduledPostLogsResponse(
            items=[
                ScheduledPostLogItem(
                    status=post.status,
                    error_message=post.error_message,
                    sent_at=post.sent_at,
                    updated_at=post.updated_at,
                )
            ],
        )
