# app/schemas/auth.py
from __future__ import annotations

import enum

from pydantic import BaseModel, Field, field_validator


class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    BLOCKED = "blocked"
    DELETED = "deleted"


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150)
    username: str | None = Field(None, min_length=3, max_length=100)
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{6,14}$")
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("full_name cannot be empty or whitespace only")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        return v

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v.strip()) < 8:
            raise ValueError("password must be at least 8 characters long")
        return v


class UserLogin(BaseModel):
    phone: str = Field(..., min_length=7, max_length=20)
    password: str = Field(..., min_length=1, max_length=128)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        return v.strip()


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class UserPublic(BaseModel):
    id: int
    full_name: str
    username: str | None = None
    phone: str
    role: UserRole = UserRole.MEMBER
    status: UserStatus = UserStatus.ACTIVE

    model_config = {"from_attributes": True}


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    message: str
    user: UserPublic
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
