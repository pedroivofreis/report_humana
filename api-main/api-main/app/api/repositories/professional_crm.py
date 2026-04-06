"""Professional CRM repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select

from app.api.models.professional_crm import ProfessionalCrm
from app.api.schemas.professional_crm import (
    ProfessionalCrmCreateRequest,
    ProfessionalCrmResponse,
    ProfessionalCrmUpdateRequest,
)
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class ProfessionalCrmRepository:
    """Professional CRM repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_all_professional_crms(self) -> list[ProfessionalCrmResponse]:
        """Get all professional CRMs."""
        logger.debug("get_all_professional_crms called")
        query = select(ProfessionalCrm)
        result = await self.db.execute(query)
        professional_crms = result.scalars().all()
        logger.debug(f"Retrieved {len(professional_crms)} professional CRMs")

        return [ProfessionalCrmResponse.model_validate(crm) for crm in professional_crms]

    async def get_professional_crm_by_id(
        self, professional_crm_id: UUID
    ) -> ProfessionalCrmResponse:
        """Get a professional CRM by id."""
        logger.debug(
            f"get_professional_crm_by_id called for professional_crm_id={professional_crm_id}"
        )

        query = select(ProfessionalCrm).where(ProfessionalCrm.id == professional_crm_id)
        result = await self.db.execute(query)
        professional_crm = result.scalar_one_or_none()
        logger.debug(f"Professional CRM found: {professional_crm is not None}")

        if not professional_crm:
            raise NotFoundException("Professional CRM not found")

        return ProfessionalCrmResponse.model_validate(professional_crm)

    async def get_professional_crms_by_user_id(
        self, user_id: UUID
    ) -> list[ProfessionalCrmResponse]:
        """Get all professional CRMs by user id."""
        logger.debug(f"get_professional_crms_by_user_id called for user_id={user_id}")
        query = select(ProfessionalCrm).where(ProfessionalCrm.user_id == user_id)
        result = await self.db.execute(query)
        professional_crms = result.scalars().all()
        logger.debug(f"Retrieved {len(professional_crms)} professional CRMs for user {user_id}")

        return [ProfessionalCrmResponse.model_validate(crm) for crm in professional_crms]

    async def create_professional_crm(
        self, professional_crm: ProfessionalCrmCreateRequest
    ) -> ProfessionalCrmResponse:
        """Create a professional CRM."""
        professional_crm_data = professional_crm.model_dump()
        new_professional_crm = ProfessionalCrm(**professional_crm_data)

        self.db.add(new_professional_crm)
        await self.db.commit()
        await self.db.refresh(new_professional_crm)

        return ProfessionalCrmResponse.model_validate(new_professional_crm)

    async def update_professional_crm(
        self, professional_crm_id: UUID, professional_crm_data: ProfessionalCrmUpdateRequest
    ) -> ProfessionalCrmResponse:
        """Update a professional CRM."""
        query = select(ProfessionalCrm).where(ProfessionalCrm.id == professional_crm_id)
        result = await self.db.execute(query)
        professional_crm = result.scalar_one_or_none()

        if not professional_crm:
            raise NotFoundException("Professional CRM not found")

        for key, value in professional_crm_data.model_dump(exclude_unset=True).items():
            setattr(professional_crm, key, value)

        await self.db.commit()
        await self.db.refresh(professional_crm)

        return ProfessionalCrmResponse.model_validate(professional_crm)

    async def delete_professional_crm(self, professional_crm_id: UUID) -> None:
        """Delete a professional CRM."""
        query = select(ProfessionalCrm).where(ProfessionalCrm.id == professional_crm_id)
        result = await self.db.execute(query)
        professional_crm = result.scalar_one_or_none()

        if not professional_crm:
            raise NotFoundException("Professional CRM not found")

        await self.db.delete(professional_crm)
        await self.db.commit()
