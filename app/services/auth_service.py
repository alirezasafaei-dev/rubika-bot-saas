"""
Authentication & authorisation service.

Uses JWT (via app.core.security) for token management and
stores refresh token hashes in the database for revocation.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db import get_db
from app.models.refresh_token import RefreshToken as RefreshTokenModel
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    UserLogin,
    UserPublic,
    UserRegister,
)

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30


class AuthService:
    """Handles user registration, login, token lifecycle."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    # ── Register ─────────────────────────────────────────────────────

    async def register(self, payload: UserRegister) -> tuple[User, str, str]:
        """Create a new user and return (user, access_token, refresh_token)."""
        # Check duplicate phone
        existing = await self.user_repo.get_by_phone(payload.phone)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "PHONE_ALREADY_EXISTS",
                    "message": "A user with this phone number already exists.",
                },
            )

        # Check duplicate username if provided
        if payload.username:
            existing_username = await self.user_repo.get_by_username(payload.username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "USERNAME_ALREADY_EXISTS",
                        "message": "This username is already taken.",
                    },
                )

        # Hash password & create user
        hashed_pw = hash_password(payload.password)
        user = await self.user_repo.create(
            full_name=payload.full_name.strip(),
            username=payload.username.strip() if payload.username else None,
            phone=payload.phone,
            password_hash=hashed_pw,
        )

        # Generate token pair
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        await self._store_refresh_token(user.id, refresh_token)

        return user, access_token, refresh_token

    # ── Login ────────────────────────────────────────────────────────

    async def login(self, payload: UserLogin) -> tuple[User, str, str]:
        """Authenticate user and return (user, access_token, refresh_token)."""
        user = await self.user_repo.get_by_phone(payload.phone)
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid phone number or password.",
                },
            )

        if user.status.value == "blocked":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "USER_BLOCKED",
                    "message": "Your account has been blocked.",
                },
            )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        await self._store_refresh_token(user.id, refresh_token)

        return user, access_token, refresh_token

    # ── Refresh ──────────────────────────────────────────────────────

    async def refresh(self, refresh_token: str) -> str:
        """Validate a refresh token and return a new access token."""
        # Decode JWT
        try:
            payload = decode_token(refresh_token)
            user_id_str: Optional[str] = payload.get("sub")
            if user_id_str is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "INVALID_REFRESH_TOKEN",
                        "message": "Invalid refresh token.",
                    },
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Invalid refresh token.",
                },
            )

        user_id = int(user_id_str)

        # Verify token is stored and not revoked
        token_hash = self._hash_token(refresh_token)
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.is_revoked == False,
        )
        result = await self.db.execute(stmt)
        stored = result.scalars().first()

        if not stored:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Refresh token has been revoked or does not exist.",
                },
            )

        # Check user exists and is active
        user = await self.user_repo.get(user_id)
        if not user or user.status.value == "deleted":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "User no longer exists.",
                },
            )

        # Issue new access token
        new_access_token = create_access_token({"sub": str(user_id)})
        return new_access_token

    # ── Logout ───────────────────────────────────────────────────────

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token."""
        token_hash = self._hash_token(refresh_token)
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.is_revoked == False,
        )
        result = await self.db.execute(stmt)
        stored = result.scalars().first()

        if not stored:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Refresh token not found or already revoked.",
                },
            )

        stored.is_revoked = True
        await self.db.commit()

    # ── Get current user ─────────────────────────────────────────────

    async def get_current_user(self, token: str) -> User:
        """Decode an access token and return the corresponding user."""
        try:
            payload = decode_token(token)
            user_id_str: Optional[str] = payload.get("sub")
            if user_id_str is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "INVALID_TOKEN",
                        "message": "Token is missing subject.",
                    },
                )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token is invalid or expired.",
                },
            )

        user_id = int(user_id_str)
        user = await self.user_repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found.",
                },
            )
        return user

    # ── Helpers ──────────────────────────────────────────────────────

    async def _store_refresh_token(self, user_id: int, token: str) -> None:
        """Persist a refresh token hash in the database."""
        token_hash = self._hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        rt = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(rt)
        await self.db.commit()

    @staticmethod
    def _hash_token(token: str) -> str:
        """Return SHA-256 hex digest of *token*."""
        return hashlib.sha256(token.encode()).hexdigest()


# ── FastAPI dependency ──────────────────────────────────────────────

async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Provide an AuthService instance wired to the current DB session."""
    return AuthService(db)
