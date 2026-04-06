from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=Any)

logger = structlog.get_logger(__name__)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: type[ModelType], db: AsyncSession):
        """Initialize the repository."""
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID, include_deleted: bool = False) -> ModelType | None:
        """Get entity by ID."""
        query = select(self.model).where(self.model.id == id)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, include_deleted: bool = False) -> Sequence[ModelType]:
        """Get all entities."""
        query = select(self.model)

        if not include_deleted and hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, entity: ModelType) -> ModelType:
        """Create new entity."""
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def delete(self, id: UUID) -> None:
        """Delete entity (hard delete)."""
        entity = await self.get_by_id(id)
        if not entity:
            return

        if hasattr(entity, "deleted_at"):
            entity.deleted_at = datetime.now(UTC)
            await self.db.flush()
        else:
            await self.db.delete(entity)

    async def update(self, id: UUID, obj_in: dict[str, Any] | Any) -> ModelType | None:
        """Update entity by ID."""
        entity = await self.get_by_id(id)
        if not entity:
            return None

        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(entity, field):
                setattr(entity, field, value)

        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def get_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        filters: dict[str, Any] | None = None,
    ) -> tuple[Sequence[ModelType], int]:
        """Get paginated results."""
        query = select(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)

        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(count_query) or 0

        # Pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return items, total

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count entities matching filters."""
        query = select(func.count()).select_from(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key) and value is not None:
                    query = query.where(getattr(self.model, key) == value)

        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        return await self.db.scalar(query) or 0

    async def exists(self, filters: dict[str, Any]) -> bool:
        """Check if entity exists."""
        query = select(1).select_from(self.model)

        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)

        if hasattr(self.model, "deleted_at"):
            query = query.where(self.model.deleted_at.is_(None))

        query = query.limit(1)
        result = await self.db.scalar(query)
        return result is not None

    async def bulk_create(self, entities: Sequence[ModelType]) -> Sequence[ModelType]:
        """Create multiple entities."""
        self.db.add_all(entities)
        await self.db.flush()
        return entities
