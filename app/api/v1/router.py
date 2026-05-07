"""
Aggregate all v1 API routers.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.channels import router as channel_router
from app.api.v1.endpoints.workspaces import router as workspace_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(workspace_router, tags=["workspaces"])
api_router.include_router(channel_router, tags=["channels"])
