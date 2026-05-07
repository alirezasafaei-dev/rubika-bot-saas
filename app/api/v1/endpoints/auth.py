# app/api/v1/endpoints/auth.py
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(
    data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    user = await service.register(data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    access, refresh = await service.login(data)

    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    access, new_refresh = await service.refresh(refresh_token)

    return TokenResponse(
        access_token=access,
        refresh_token=new_refresh,
    )


@router.post("/logout")
async def logout(
    refresh_token: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    service = AuthService(db)
    await service.logout(refresh_token)
    return {"success": True}


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
