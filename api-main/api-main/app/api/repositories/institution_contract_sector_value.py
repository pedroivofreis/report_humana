"""Institution contract sector value repository."""

from datetime import date
from uuid import UUID

from fastapi import Depends
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.models.institution_contract_sector_value import InstitutionContractSectorValue
from app.api.models.sectors import Sector
from app.api.repositories.base import BaseRepository
from app.db.session import get_db_session


class InstitutionContractSectorValueRepository(BaseRepository[InstitutionContractSectorValue]):
    """Institution Contract Sector Value repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=InstitutionContractSectorValue, db=db)

    async def get_by_contract(self, contract_id: UUID) -> list[InstitutionContractSectorValue]:
        """Get all sector values for a specific contract."""
        query = (
            select(InstitutionContractSectorValue)
            .options(
                selectinload(InstitutionContractSectorValue.sector).selectinload(
                    Sector.contract_values
                ),
            )
            .where(InstitutionContractSectorValue.institution_contract_id == contract_id)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_active_by_contract_and_sector(
        self, contract_id: UUID, sector_id: UUID
    ) -> InstitutionContractSectorValue | None:
        """Get an active sector value (in validity period) for a specific contract and sector."""
        today = date.today()
        query = (
            select(InstitutionContractSectorValue)
            .options(
                selectinload(InstitutionContractSectorValue.sector).selectinload(
                    Sector.contract_values
                )
            )
            .where(
                InstitutionContractSectorValue.institution_contract_id == contract_id,
                InstitutionContractSectorValue.sector_id == sector_id,
                InstitutionContractSectorValue.start_date <= today,
                or_(
                    InstitutionContractSectorValue.end_date.is_(None),
                    InstitutionContractSectorValue.end_date >= today,
                ),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_with_details(self, value_id: UUID) -> InstitutionContractSectorValue | None:
        """Get a specific value with details."""
        query = (
            select(InstitutionContractSectorValue)
            .options(
                selectinload(InstitutionContractSectorValue.sector).selectinload(
                    Sector.contract_values
                ),
            )
            .where(InstitutionContractSectorValue.id == value_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
