"""Institution Contract repository."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.models.institution_contract import InstitutionContract
from app.api.models.user import User
from app.api.repositories.base import BaseRepository
from app.db.session import get_db_session


class InstitutionContractRepository(BaseRepository[InstitutionContract]):
    """Institution Contract repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        super().__init__(model=InstitutionContract, db=db)

    async def get_with_details(self, contract_id: UUID) -> InstitutionContract | None:
        """Get a contract by id with relations loaded."""
        query = (
            select(InstitutionContract)
            .options(
                selectinload(InstitutionContract.institution),
                selectinload(InstitutionContract.user).selectinload(User.complementary_data),
            )
            .where(InstitutionContract.id == contract_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all_with_details(self) -> list[InstitutionContract]:
        """Get all contracts with relations loaded."""
        query = select(InstitutionContract).options(
            selectinload(InstitutionContract.institution),
            selectinload(InstitutionContract.user).selectinload(User.complementary_data),
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_institution(self, institution_id: UUID) -> list[InstitutionContract]:
        """Get all contracts for an institution."""
        query = (
            select(InstitutionContract)
            .options(
                selectinload(InstitutionContract.institution),
                selectinload(InstitutionContract.user).selectinload(User.complementary_data),
            )
            .where(InstitutionContract.institution_id == institution_id)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
