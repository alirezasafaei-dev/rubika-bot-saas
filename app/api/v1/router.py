from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    auto_replies,
    channels,
    filters,
    scheduled_posts,
    webhooks,
    workspaces,
)

api_router = APIRouter()
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(workspaces.router)
api_router.include_router(channels.router)
api_router.include_router(auto_replies.router)
api_router.include_router(filters.router)
api_router.include_router(scheduled_posts.router)
api_router.include_router(webhooks.router)
