from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from app.core.errors import ConflictError, ErrorCode, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenResponse, UserRegister

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.user import User


class AuthService:
    def __init__(self, db: AsyncSession, user_repo: UserRepository) -> None:
        self.db = db
        self.user_repo = user_repo

    async def register(self, payload: UserRegister) -> User:
        phone = payload.phone.strip()

        existing_user = await self.user_repo.get_by_phone(phone)
        if existing_user is not None:
            raise ConflictError(
                ErrorCode.USER_ALREADY_EXISTS,
                f"User with phone {phone} already exists",
            )

        username = payload.username.strip() if payload.username else None
        if username is not None:
            existing_user_by_username = await self.user_repo.get_by_username(username)
            if existing_user_by_username is not None:
                raise ConflictError(
                    ErrorCode.USER_ALREADY_EXISTS,
                    f"User with username {username} already exists",
                )

        user = await self.user_repo.create(
            **{
                "full_name": payload.full_name.strip(),
                "username": username,
                "phone": phone,
                "hashed_password": hash_password(payload.password),
            }
        )
        return user

    async def login(self, phone: str, password: str) -> TokenResponse:
        user = await self.user_repo.get_by_phone(phone.strip())
        if user is None or not verify_password(password, user.hashed_password):
            raise UnauthorizedError(
                ErrorCode.INVALID_CREDENTIALS,
                "Invalid credentials",
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        refresh_token_row = RefreshToken(
            user_id=user.id,
            token_hash=self._hash_token(refresh_token),
            expires_at=self._get_refresh_token_expiry(),
        )
        self.db.add(refresh_token_row)
        await self.db.commit()
        await self.db.refresh(refresh_token_row)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_refresh_token(refresh_token)
        except ValueError as exc:
            raise UnauthorizedError(
                ErrorCode.INVALID_TOKEN,
                "Invalid refresh token",
            ) from exc

        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError(
                ErrorCode.INVALID_TOKEN,
                "Invalid refresh token payload",
            )

        token_hash = self._hash_token(refresh_token)
        user = await self.user_repo.get_by_id(int(user_id))
        if user is None:
            raise UnauthorizedError(ErrorCode.USER_NOT_FOUND, "User not found")

        stored_token = await self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.user_id == user.id,
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked.is_(False),
            )
        )
        if stored_token is None or stored_token.is_expired():
            raise UnauthorizedError(
                ErrorCode.TOKEN_EXPIRED,
                "Invalid or expired refresh token",
            )

        new_access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        stored_token.token_hash = self._hash_token(new_refresh_token)
        stored_token.expires_at = self._get_refresh_token_expiry()
        await self.db.commit()
        await self.db.refresh(stored_token)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    async def logout(self, user: User) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.user_id == user.id)
        )
        await self.db.commit()

    @staticmethod
    def _get_refresh_token_expiry() -> datetime:
        from app.core.config import settings

        return datetime.now(UTC) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )

    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
