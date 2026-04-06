"""Profession repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select

from app.api.models.profession import Profession
from app.api.schemas.profession import (
    ProfessionCreateRequest,
    ProfessionResponse,
    ProfessionUpdateRequest,
)
from app.core.exceptions import NotFoundException, ResourceAlreadyExistsException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class ProfessionRepository:
    """Profession repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_professions(self, include_inactive: bool = False) -> list[ProfessionResponse]:
        """Get all professions."""
        logger.debug("get_professions called")
        query = select(Profession)

        if not include_inactive:
            query = query.where(Profession.is_active)

        result = await self.db.execute(query)
        professions = result.scalars().all()
        logger.debug(f"Retrieved {len(professions)} professions")

        return [ProfessionResponse.model_validate(profession) for profession in professions]

    async def get_profession_by_id(
        self, profession_id: UUID, with_specialties: bool = False
    ) -> ProfessionResponse | None:
        """Get a profession by id."""
        logger.debug(f"get_profession_by_id called for profession_id={profession_id}")

        query = select(Profession).where(Profession.id == profession_id)

        result = await self.db.execute(query)
        profession = result.scalar_one_or_none()
        logger.debug(f"Profession found: {profession is not None}")

        if not profession:
            raise NotFoundException("Profession not found")

        return ProfessionResponse.model_validate(profession)

    async def get_profession_by_name(self, name: str) -> ProfessionResponse | None:
        """Get a profession by name."""
        logger.debug(f"get_profession_by_name called for name={name}")
        result = await self.db.execute(select(Profession).where(Profession.name == name))
        profession = result.scalar_one_or_none()
        logger.debug(f"Profession found: {profession is not None}")

        if not profession:
            return None

        return ProfessionResponse.model_validate(profession)

    async def create_profession(self, profession: ProfessionCreateRequest) -> ProfessionResponse:
        """Create a profession."""
        logger.debug("create_profession called")

        existing = await self.get_profession_by_name(profession.name)
        if existing:
            raise ResourceAlreadyExistsException(resource_name="Profissão")

        profession_data = profession.model_dump()
        new_profession = Profession(**profession_data)

        self.db.add(new_profession)
        await self.db.commit()
        await self.db.refresh(new_profession)

        return ProfessionResponse.model_validate(new_profession)

    async def update_profession(
        self, profession_id: UUID, profession_data: ProfessionUpdateRequest
    ) -> ProfessionResponse:
        """Update a profession."""
        logger.debug(f"update_profession called for profession_id={profession_id}")

        result = await self.db.execute(select(Profession).where(Profession.id == profession_id))
        profession = result.scalar_one_or_none()

        if not profession:
            raise NotFoundException("Profession not found")

        if profession_data.name and profession_data.name != profession.name:
            existing = await self.get_profession_by_name(profession_data.name)
            if existing:
                raise ResourceAlreadyExistsException(resource_name="Profissão")

        for key, value in profession_data.model_dump(exclude_unset=True).items():
            setattr(profession, key, value)

        await self.db.commit()
        await self.db.refresh(profession)

        return ProfessionResponse.model_validate(profession)

    async def delete_profession(self, profession_id: UUID) -> None:
        """Delete a profession."""
        logger.debug(f"delete_profession called for profession_id={profession_id}")
        result = await self.db.execute(select(Profession).where(Profession.id == profession_id))
        profession = result.scalar_one_or_none()

        if not profession:
            raise NotFoundException("Profession not found")

        await self.db.delete(profession)
        await self.db.commit()
