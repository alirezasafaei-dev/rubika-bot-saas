# app/core/security.py
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def hash_password(password: str) -> str:
    """Alias for compatibility with older service code."""
    return get_password_hash(password)


def _build_token_payload(
    data: dict[str, Any],
    expires_delta: timedelta,
    token_type: str,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    to_encode = data.copy()
    to_encode.update(
        {
            "exp": expire,
            "iat": now,
            "nbf": now,
            "jti": str(uuid4()),
            "type": token_type,
        }
    )
    return to_encode


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token."""
    payload = _build_token_payload(
        data=data,
        expires_delta=expires_delta or timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
    )
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT refresh token."""
    payload = _build_token_payload(
        data=data,
        expires_delta=expires_delta or timedelta(days=settings.refresh_token_expire_days),
        token_type="refresh",
    )
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as e:
        raise ValueError(f"Token decode error: {e}") from e


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode token and enforce access token type."""
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise ValueError("Invalid token type: access token required")
    return payload


def decode_refresh_token(token: str) -> dict[str, Any]:
    """Decode token and enforce refresh token type."""
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type: refresh token required")
    return payload
