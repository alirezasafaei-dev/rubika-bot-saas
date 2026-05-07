# app/core/security.py
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import settings

password_hasher = PasswordHasher(
    time_cost=settings.argon2_time_cost,
    memory_cost=settings.argon2_memory_cost,
    parallelism=settings.argon2_parallelism,
    hash_len=settings.argon2_hash_len,
    salt_len=settings.argon2_salt_len,
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return password_hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return password_hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def _build_token(
    user_id: int,
    token_type: str,
    expires_delta: timedelta,
    jti: str | None = None,
) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if jti is not None:
        payload["jti"] = jti
    return jwt.encode(
        payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    return _build_token(
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    """Create JWT refresh token with unique JTI."""
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    jti = str(uuid4())
    token = _build_token(
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        jti=jti,
    )
    return token, jti, expires_at


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify JWT token."""
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    return dict(payload)
