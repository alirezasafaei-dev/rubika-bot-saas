# app/services/auth_service.py
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.refresh_token import RefreshToken as RefreshTokenModel
from app.models.user import User, UserStatus
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserLogin, UserRegister


class AuthService:
    """Handles user registration, login, token lifecycle, and current-user resolution."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, payload: UserRegister) -> tuple[User, str, str]:
        """Create a new user and return (user, access_token, refresh_token)."""
        phone = payload.phone.strip()
        username = payload.username.strip() if payload.username else None
        full_name = payload.full_name.strip()

        existing = await self.user_repo.get_by_phone(phone)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "PHONE_ALREADY_EXISTS",
                    "message": "A user with this phone number already exists.",
                },
            )

        if username:
            existing_username = await self.user_repo.get_by_username(username)
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "code": "USERNAME_ALREADY_EXISTS",
                        "message": "This username is already taken.",
                    },
                )

        hashed_pw = hash_password(payload.password)

        user = await self.user_repo.create(
            full_name=full_name,
            username=username,
            phone=phone,
            hashed_password=hashed_pw,
        )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        await self._store_refresh_token(user.id, refresh_token)

        return user, access_token, refresh_token

    async def login(self, payload: UserLogin) -> tuple[User, str, str]:
        """Authenticate user and return (user, access_token, refresh_token)."""
        phone = payload.phone.strip()
        user = await self.user_repo.get_by_phone(phone)

        if not user or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_CREDENTIALS",
                    "message": "Invalid phone number or password.",
                },
            )

        if user.status == UserStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "USER_BLOCKED",
                    "message": "Your account has been blocked.",
                },
            )

        if user.status == UserStatus.DELETED or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "USER_INACTIVE",
                    "message": "This account is inactive.",
                },
            )

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        await self._store_refresh_token(user.id, refresh_token)

        return user, access_token, refresh_token

    async def refresh(self, refresh_token: str) -> str:
        """Validate a refresh token and return a new access token."""
        try:
            payload = decode_refresh_token(refresh_token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Invalid or expired refresh token.",
                },
            )

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Invalid refresh token.",
                },
            )

        try:
            user_id = int(user_id_str)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Invalid refresh token subject.",
                },
            )

        token_hash = self._hash_token(refresh_token)
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.is_revoked.is_(False),
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

        now = datetime.now(timezone.utc)
        expires_at = stored.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= now:
            stored.is_revoked = True
            await self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "Refresh token has expired.",
                },
            )

        user = await self.user_repo.get(user_id)
        if not user or user.status in {UserStatus.DELETED, UserStatus.BLOCKED} or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_REFRESH_TOKEN",
                    "message": "User is no longer active.",
                },
            )

        new_access_token = create_access_token({"sub": str(user_id)})
        return new_access_token

    async def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token."""
        token_hash = self._hash_token(refresh_token)
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash,
            RefreshTokenModel.is_revoked.is_(False),
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

    async def get_current_user(self, token: str) -> User:
        """Decode an access token and return the corresponding user."""
        try:
            payload = decode_access_token(token)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token is invalid or expired.",
                },
            )

        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token is missing subject.",
                },
            )

        try:
            user_id = int(user_id_str)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "INVALID_TOKEN",
                    "message": "Token subject is invalid.",
                },
            )

        user = await self.user_repo.get(user_id)
        if not user or user.status == UserStatus.DELETED:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "USER_NOT_FOUND",
                    "message": "User not found.",
                },
            )

        if user.status == UserStatus.BLOCKED or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "USER_INACTIVE",
                    "message": "User is inactive.",
                },
            )

        return user

    async def _store_refresh_token(self, user_id: int, token: str) -> None:
        """Persist a refresh token hash in the database."""
        token_hash = self._hash_token(token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

        rt = RefreshTokenModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(rt)
        await self.db.commit()

    @staticmethod
    def _hash_token(token: str) -> str:
        """Return SHA-256 hex digest of token."""
        return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """Provide an AuthService instance wired to the current DB session."""
    return AuthService(db)
