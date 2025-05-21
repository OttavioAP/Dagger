from typing import TypeVar, Generic, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import UUID
from uuid import UUID as PyUUID
from app.services.database_service import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository providing common CRUD operations
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def _convert_id(self, id: Any) -> Any:
        """Convert ID to appropriate type based on model's ID column type"""
        id_column = self.model.__table__.c.id
        if isinstance(id_column.type, UUID):
            return PyUUID(str(id)) if isinstance(id, str) else id
        return id

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def get_by_id(
        self, db: AsyncSession, id: str | PyUUID
    ) -> Optional[ModelType]:
        id_value = self._convert_id(id)
        query = select(self.model).where(self.model.id == id_value)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def update(
        self, db: AsyncSession, *, id: str | PyUUID, **kwargs
    ) -> Optional[ModelType]:
        id_value = self._convert_id(id)
        query = update(self.model).where(self.model.id == id_value).values(**kwargs)
        await db.execute(query)
        await db.commit()
        return await self.get_by_id(db, id)

    async def delete(self, db: AsyncSession, *, id: str | PyUUID) -> bool:
        id_value = self._convert_id(id)
        query = delete(self.model).where(self.model.id == id_value)
        result = await db.execute(query)
        await db.commit()
        return result.rowcount > 0

    async def filter(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100, **kwargs
    ) -> List[ModelType]:
        query = select(self.model).filter_by(**kwargs).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
