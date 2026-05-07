"""
User-specific repository.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data-access layer for the User model."""

    def __init__(self, db) -> None:
        super().__init__(db, User)

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Find a user by phone number."""
        stmt = select(User).where(User.phone == phone)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, username: str) -> Optional[User]:
        """Find a user by username."""
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalars().first()
