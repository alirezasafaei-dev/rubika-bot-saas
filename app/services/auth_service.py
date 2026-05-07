# app/services/auth_service.py
from datetime import datetime, timedelta, timezone
from typing import Optional
import secrets

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from argon2 import PasswordHasher

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.errors import (
    AppException,
    ErrorCode,
)


class AuthService:
    def __init__(self):
        self.pwd_hasher = PasswordHasher()

    def _hash_password(self, password: str) -> str:
        return self.pwd_hasher.hash(password)

    def _verify_password(self, hashed: str, password: str) -> bool:
        try:
            self.pwd_hasher.verify(hashed, password)
            return True
        except Exception:
            return False

    def _generate_access_token(self, user_id: int) -> str:
        # Simple JWT-like simulation (replace with real JWT)
        return secrets.token_hex(32)

    def _generate_refresh_token(self) -> str:
        return secrets.token_urlsafe(48)

    async def register(
        self,
        db: AsyncSession,
        email: str,
        password: str,
        full_name: str,
    ) -> User:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise AppException(ErrorCode.EMAIL_ALREADY_EXISTS)

        hashed = self._hash_password(password)
        user = User(email=email, hashed_password=hashed, full_name=full_name)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    async def login(
        self,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> tuple[str, str]:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user or not self._verify_password(user.hashed_password, password):
            raise AppException(ErrorCode.INVALID_CREDENTIALS)

        access_token = self._generate_access_token(user.id)
        refresh_token_str = self._generate_refresh_token()

        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user.id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )

        db.add(refresh_token)
        await db.commit()

        return access_token, refresh_token_str

    async def refresh(
        self,
        db: AsyncSession,
        refresh_token_str: str,
    ) -> tuple[str, str]:
        stmt = select(RefreshToken).where(
            RefreshToken.token == refresh_token_str
        )
        result = await db.execute(stmt)
        token_row = result.scalar_one_or_none()

        if not token_row:
            raise AppException(ErrorCode.INVALID_REFRESH_TOKEN)

        if token_row.revoked:
            raise AppException(ErrorCode.REFRESH_TOKEN_REVOKED)

        if token_row.expires_at < datetime.now(timezone.utc):
            raise AppException(ErrorCode.REFRESH_TOKEN_EXPIRED)

        # revoke old
        token_row.revoked = True

        new_refresh_token = self._generate_refresh_token()
        new_row = RefreshToken(
            token=new_refresh_token,
            user_id=token_row.user_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )

        db.add(new_row)
        await db.commit()

        access_token = self._generate_access_token(token_row.user_id)
        return access_token, new_refresh_token

    async def logout(
        self,
        db