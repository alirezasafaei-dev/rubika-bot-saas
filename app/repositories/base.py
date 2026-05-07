# app/repositories/base.py
from typing import Generic, Sequence, TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictException(detail=str(e))
        await self.session.refresh(instance)
        return instance

    async def get(self, **kwargs) -> ModelType:
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        instance = result.scalar_one_or_none()
        if instance is None:
            raise NotFoundException(detail=f"{self.model.__name__} not found")
        return instance

    async def get_multi(self, offset: int = 0, limit: int = 100, **kwargs) -> Sequence[ModelType]:
        """Alias for list() - متد سازگار با کدهای قبلی"""
        return await self.list(offset=offset, limit=limit, **kwargs)

    async def list(self, offset: int = 0, limit: int = 100, **kwargs) -> Sequence[ModelType]:
        query = select(self.model).filter_by(**kwargs).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, instance: ModelType, **kwargs) -> ModelType:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictException(detail=str(e))
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: ModelType) -> None:
        await self.session.delete(instance)
        await self.session.commit()

    async def soft_delete(self, **filters) -> None:
        """حذف نرم با ست کردن deleted_at"""
        instance = await self.get(**filters)
        instance.deleted_at = datetime.utcnow()
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise ConflictException(detail=str(e))

    async def count(self, **filters) -> int:
        from sqlalchemy import func, select as sel_count
        query = sel_count(func.count()).select_from(self.model)
        for attr, value in filters.items():
            query = query.where(getattr(self.model, attr) == value)
        result = await self.session.execute(query)
        return result.scalar_one()
