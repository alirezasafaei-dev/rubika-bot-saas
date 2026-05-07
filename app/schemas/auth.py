"""
Auth schemas: register, login, token refresh, current user.
"""
from __future__ import annotations

import enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class UserRole(str, enum.Enum):
    """User roles within the system."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class UserStatus(str, enum.Enum):
    """User account status."""
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"


# ─── Request Schemas ────────────────────────────────────────────────

class UserRegister(BaseModel):
    """Register a new user."""
    full_name: str = Field(..., min_length=1, max_length=150)
    username: Optional[str] = Field(None, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{6,14}$")  # E.164 format
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def full_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("full_name cannot be empty or whitespace only")
        return v.strip()


class UserLogin(BaseModel):
    """User login with phone and password."""
    phone: str = Field(...)
    password: str = Field(...)


class RefreshTokenRequest(BaseModel):
    """Request a new access token using a refresh token."""
    refresh_token: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    """Invalidate a refresh token on logout."""
    refresh_token: str = Field(..., min_length=1)


# ─── Response Schemas ───────────────────────────────────────────────

class UserPublic(BaseModel):
    """Public user info returned in API responses."""
    id: int
    full_name: str
    username: Optional[str] = None
    phone: str
    role: UserRole = UserRole.MEMBER
    status: UserStatus = UserStatus.ACTIVE

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    """Access + refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    """Standard auth response with tokens and user info."""
    message: str
    user: UserPublic
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshResponse(BaseModel):
    """Response for token refresh."""
    message: str
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
