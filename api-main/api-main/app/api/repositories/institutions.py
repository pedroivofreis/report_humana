"""Institution repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.institutions import Institution
from app.api.models.sectors import Sector
from app.api.repositories.base import BaseRepository
from app.api.schemas.institution_contract import InstitutionContractSimpleResponse
from app.api.schemas.institutions import InstitutionRequest, InstitutionResponse
from app.core.exceptions import ResourceNotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class InstitutionRepository(BaseRepository[Institution]):
    """Institution repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=Institution, db=db)

    async def get_institutions(self, include_deleted: bool = False) -> list[InstitutionResponse]:
        """Get all institutions."""
        query = (
            select(Institution)
            .options(selectinload(Institution.address))
            .options(selectinload(Institution.sectors).selectinload(Sector.contract_values))
            .options(selectinload(Institution.contracts))
        )

        if not include_deleted:
            query = query.where(Institution.deleted_at.is_(None))

        result = await self.db.execute(query)
        institutions = result.scalars().unique().all()

        responses = []
        for institution in institutions:
            institution.sectors = [s for s in institution.sectors if s.deleted_at is None]
            response = InstitutionResponse.model_validate(institution)
            response.lst_contract = (
                InstitutionContractSimpleResponse.model_validate(institution.lst_contract)
                if institution.lst_contract
                else None
            )
            responses.append(response)
        return responses

    async def get_institution_by_id(
        self, institution_id: UUID, include_deleted: bool = False
    ) -> InstitutionResponse:
        """Get a institution by id."""
        query = (
            select(Institution)
            .options(selectinload(Institution.address))
            .options(selectinload(Institution.sectors).selectinload(Sector.contract_values))
            .options(selectinload(Institution.contracts))
            .where(Institution.id == institution_id)
        )

        if not include_deleted:
            query = query.where(Institution.deleted_at.is_(None))

        result = await self.db.execute(query)
        institution = result.scalars().unique().one_or_none()

        if institution is None:
            return None

        institution.sectors = [s for s in institution.sectors if s.deleted_at is None]

        response = InstitutionResponse.model_validate(institution)
        response.lst_contract = (
            InstitutionContractSimpleResponse.model_validate(institution.lst_contract)
            if institution.lst_contract
            else None
        )
        return response

    async def create_institution(self, institution: InstitutionRequest) -> InstitutionResponse:
        """Create a institution."""
        new_institution = Institution(**institution.model_dump(exclude={"address"}))
        await self.create(new_institution)
        await self.db.flush()
        return await self.get_institution_by_id(new_institution.id)

    async def update_institution(
        self, institution_id: UUID, institutionData: InstitutionRequest
    ) -> InstitutionResponse:
        """Update a institution."""

        institution = await self.get_by_id(institution_id)
        if not institution:
            raise ResourceNotFoundException(resource_name="institution", resource_id=institution_id)

        for key, value in institutionData.model_dump(exclude={"address", "address_id"}).items():
            setattr(institution, key, value)

        await self.db.commit()
        return await self.get_institution_by_id(institution_id)

    async def delete_institution(self, institution_id: UUID) -> None:
        """Soft delete a institution."""
        institution = await self.get_by_id(institution_id)

        if not institution:
            raise ResourceNotFoundException(resource_name="institution", resource_id=institution_id)

        await self.delete(institution_id)
