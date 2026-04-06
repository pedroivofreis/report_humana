"""Specialty repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.specialty import Specialty
from app.api.schemas.specialty import (
    SpecialtyCreateRequest,
    SpecialtyResponse,
    SpecialtyUpdateRequest,
)
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class SpecialtyRepository:
    """Specialty repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_specialties(
        self, include_inactive: bool = False
    ) -> list[SpecialtyResponse]:
        """Get all specialties."""
        logger.debug("get_specialties called")
        query = select(Specialty)

        if not include_inactive:
            query = query.where(Specialty.is_active)

        result = await self.db.execute(query)
        specialties = result.scalars().all()
        logger.debug(f"Retrieved {len(specialties)} specialties")

        return [SpecialtyResponse.model_validate(specialty) for specialty in specialties]

    async def get_specialty_by_id(
        self, specialty_id: UUID
    ) -> SpecialtyResponse | None:
        """Get a specialty by id."""
        logger.debug(f"get_specialty_by_id called for specialty_id={specialty_id}")

        query = select(Specialty).where(Specialty.id == specialty_id)

        result = await self.db.execute(query)
        specialty = result.scalar_one_or_none()
        logger.debug(f"Specialty found: {specialty is not None}")

        if not specialty:
            raise NotFoundException("Specialty not found")

        return SpecialtyResponse.model_validate(specialty)


    async def create_specialty(self, specialty: SpecialtyCreateRequest) -> SpecialtyResponse:
        """Create a specialty."""
        logger.debug("create_specialty called")

        specialty_data = specialty.model_dump()
        new_specialty = Specialty(**specialty_data)

        self.db.add(new_specialty)
        await self.db.commit()
        await self.db.refresh(new_specialty)

        return SpecialtyResponse.model_validate(new_specialty)

    async def update_specialty(
        self, specialty_id: UUID, specialty_data: SpecialtyUpdateRequest
    ) -> SpecialtyResponse:
        """Update a specialty."""
        logger.debug(f"update_specialty called for specialty_id={specialty_id}")

        result = await self.db.execute(select(Specialty).where(Specialty.id == specialty_id))
        specialty = result.scalar_one_or_none()

        if not specialty:
            raise NotFoundException("Specialty not found")

        for key, value in specialty_data.model_dump(exclude_unset=True).items():
            setattr(specialty, key, value)

        await self.db.commit()
        await self.db.refresh(specialty)

        return SpecialtyResponse.model_validate(specialty)

    async def delete_specialty(self, specialty_id: UUID) -> None:
        """Delete a specialty."""
        logger.debug(f"delete_specialty called for specialty_id={specialty_id}")
        result = await self.db.execute(select(Specialty).where(Specialty.id == specialty_id))
        specialty = result.scalar_one_or_none()

        if not specialty:
            raise NotFoundException("Specialty not found")

        await self.db.delete(specialty)
        await self.db.commit()
