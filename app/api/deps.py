# app/api/deps.py
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppException, ErrorCode
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    token = credentials.credentials

    payload = decode_token(token)
    if not payload:
        raise AppException(ErrorCode.INVALID_TOKEN)

    user_id = payload.get("sub")
    if not user_id:
        raise AppException(ErrorCode.INVALID_TOKEN)

    stmt = select(User).where(User.id == int(user_id))
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise AppException(ErrorCode.USER_NOT_FOUND)

    return user
