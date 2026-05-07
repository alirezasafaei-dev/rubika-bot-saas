"""
Auth API endpoints: register, login, refresh, me, logout.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.schemas.auth import (
    AuthResponse,
    LogoutRequest,
    MessageResponse,
    RefreshResponse,
    RefreshTokenRequest,
    UserLogin,
    UserPublic,
    UserRegister,
)
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/auth", tags=["auth"])
security_scheme = HTTPBearer(auto_error=False)


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    payload: UserRegister,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Register a new user account."""
    user, access_token, refresh_token = await service.register(payload)
    return AuthResponse(
        message="User registered successfully",
        user=UserPublic.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: UserLogin,
    service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    """Authenticate with phone + password."""
    user, access_token, refresh_token = await service.login(payload)
    return AuthResponse(
        message="Login successful",
        user=UserPublic.model_validate(user),
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    payload: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
) -> RefreshResponse:
    """Obtain a new access token via a valid refresh token."""
    new_access_token = await service.refresh(payload.refresh_token)
    return RefreshResponse(
        message="Token refreshed",
        access_token=new_access_token,
    )


@router.get("/me", response_model=UserPublic)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserPublic:
    """Return the currently authenticated user's profile."""
    if credentials is None:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authorization header required."},
        )
    user = await service.get_current_user(credentials.credentials)
    return UserPublic.model_validate(user)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: LogoutRequest,
    service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """Revoke a refresh token (logout)."""
    await service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out successfully")
