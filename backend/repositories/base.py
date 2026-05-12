from typing import Generic, TypeVar, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from backend.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic repository for database operations."""

    def __init__(self, model: type[ModelType]):
        self.model = model

    async def create(self, db: AsyncSession, obj: CreateSchemaType, **kwargs) -> ModelType:
        """Create a new record."""
        obj_data = obj.model_dump() if hasattr(obj, "model_dump") else obj.__dict__
        obj_data.update(kwargs)
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get record by ID."""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[dict] = None
    ) -> tuple[List[ModelType], int]:
        """Get all records with pagination and filtering."""
        query = select(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        # Get count
        count_result = await db.execute(select(func.count()).select_from(self.model))
        total = count_result.scalar() or 0

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all(), total

    async def update(self, db: AsyncSession, id: Any, obj: UpdateSchemaType) -> Optional[ModelType]:
        """Update a record."""
        db_obj = await self.get(db, id)
        if not db_obj:
            return None

        obj_data = obj.model_dump(exclude_unset=True) if hasattr(obj, "model_dump") else obj.__dict__
        for key, value in obj_data.items():
            setattr(db_obj, key, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """Delete a record."""
        db_obj = await self.get(db, id)
        if not db_obj:
            return False

        await db.delete(db_obj)
        await db.commit()
        return True

    async def filter(self, db: AsyncSession, **kwargs) -> List[ModelType]:
        """Filter records by multiple criteria."""
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)

        result = await db.execute(query)
        return result.scalars().all()

    async def exists(self, db: AsyncSession, **kwargs) -> bool:
        """Check if record exists."""
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        result = await db.execute(query.limit(1))
        return result.scalars().first() is not None
