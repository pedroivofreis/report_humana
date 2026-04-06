"""Professional Location Binding repository."""

import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.models.professional_location_binding import ProfessionalLocationBinding
from app.api.models.professional_location_sector import ProfessionalLocationSector
from app.api.models.sectors import Sector
from app.api.repositories.base import BaseRepository
from app.db.session import AsyncSession, get_db_session

logger = logging.getLogger(__name__)


class ProfessionalLocationBindingRepository(BaseRepository[ProfessionalLocationBinding]):
    """Professional Location Binding repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=ProfessionalLocationBinding, db=db)

    def _get_base_query(self):
        """Returns the base query with eager loaded relationships."""
        return select(ProfessionalLocationBinding).options(
            selectinload(ProfessionalLocationBinding.institution),
            selectinload(ProfessionalLocationBinding.sectors)
                .selectinload(ProfessionalLocationSector.sector)
                .selectinload(Sector.contract_values)
        )

    async def get_by_id_with_relations(self, binding_id: UUID) -> ProfessionalLocationBinding | None:
        """Fetch binding with sectors and institution eager loaded."""
        query = self._get_base_query().where(ProfessionalLocationBinding.id == binding_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> list[ProfessionalLocationBinding]:
        """Fetch all bindings for a given professional."""
        query = self._get_base_query().where(ProfessionalLocationBinding.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all_bindings(self) -> list[ProfessionalLocationBinding]:
        """Fetch all bindings."""
        query = self._get_base_query()
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def check_duplicate(self, user_id: UUID, institution_id: UUID) -> bool:
        """Check if a binding already exists for this professional and location."""
        stmt = select(ProfessionalLocationBinding).where(
            ProfessionalLocationBinding.user_id == user_id,
            ProfessionalLocationBinding.institution_id == institution_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def find_sectors(self, sector_ids: list[UUID], institution_id: UUID) -> list:
        """Helper to find valid sectors belonging to the given institution."""
        # Using late import to avoid circular dependency
        from app.api.models.sectors import Sector
        
        stmt = select(Sector).where(
            Sector.id.in_(sector_ids), 
            Sector.institution_id == institution_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def replace_sectors(self, binding_id: UUID, sector_ids: list[UUID]) -> None:
        """Replace existing sectors for a binding with new ones."""
        # Delete old sectors
        stmt_delete = select(ProfessionalLocationSector).where(ProfessionalLocationSector.binding_id == binding_id)
        del_result = await self.db.execute(stmt_delete)
        for old_sector in del_result.scalars().all():
            await self.db.delete(old_sector)
            
        await self.db.flush()
            
        # Add new sectors
        for sector_id in sector_ids:
            new_sector = ProfessionalLocationSector(
                binding_id=binding_id,
                sector_id=sector_id,
            )
            self.db.add(new_sector)
            
        await self.db.flush()
