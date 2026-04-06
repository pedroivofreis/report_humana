"""Bank account repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select

from app.api.models.bank_account import BankAccount
from app.api.schemas.bank_account import (
    BankAccountCreateRequest,
    BankAccountResponse,
    BankAccountUpdateRequest,
)
from app.core.exceptions import NotFoundException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class BankAccountRepository:
    """Bank account repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_bank_accounts(self) -> list[BankAccountResponse]:
        """Get all bank accounts."""
        logger.debug("get_bank_accounts called")
        result = await self.db.execute(select(BankAccount))
        bank_accounts = result.scalars().all()
        logger.debug(f"Retrieved {len(bank_accounts)} bank accounts")

        return [BankAccountResponse.model_validate(bank_account) for bank_account in bank_accounts]

    async def get_bank_account_by_id(self, bank_account_id: UUID) -> BankAccountResponse | None:
        """Get a bank account by id."""
        logger.debug(f"get_bank_account_by_id called for bank_account_id={bank_account_id}")
        result = await self.db.execute(select(BankAccount).where(BankAccount.id == bank_account_id))
        bank_account = result.scalar_one_or_none()
        logger.debug(f"Bank account found: {bank_account is not None}")

        if not bank_account:
            raise NotFoundException("Bank account not found")

        return BankAccountResponse.model_validate(bank_account)

    async def get_bank_accounts_by_user_id(self, user_id: UUID) -> list[BankAccountResponse]:
        """Get bank accounts by user id."""
        logger.debug(f"get_bank_accounts_by_user_id called for user_id={user_id}")
        result = await self.db.execute(select(BankAccount).where(BankAccount.user_id == user_id))
        bank_accounts = result.scalars().all()
        logger.debug(f"Found {len(bank_accounts)} bank accounts")

        return [BankAccountResponse.model_validate(bank_account) for bank_account in bank_accounts]

    async def get_main_bank_account_by_user_id(self, user_id: UUID) -> BankAccountResponse | None:
        """Get main bank account by user id."""
        logger.debug(f"get_main_bank_account_by_user_id called for user_id={user_id}")
        result = await self.db.execute(
            select(BankAccount).where(BankAccount.user_id == user_id, BankAccount.is_main)
        )
        bank_account = result.scalar_one_or_none()
        logger.debug(f"Main bank account found: {bank_account is not None}")

        if not bank_account:
            return None

        return BankAccountResponse.model_validate(bank_account)

    async def get_bank_account_by_data(
        self,
        user_id: UUID,
        bank_code: str,
        agency: str,
        account_number: str,
        account_digit: str,
        account_type: str,
    ) -> BankAccountResponse | None:
        """Get bank account by data."""
        logger.debug(f"get_bank_account_by_data called for user_id={user_id}")
        result = await self.db.execute(
            select(BankAccount).where(
                BankAccount.user_id == user_id,
                BankAccount.bank_code == bank_code,
                BankAccount.agency == agency,
                BankAccount.account_number == account_number,
                BankAccount.account_digit == account_digit,
                BankAccount.account_type == account_type,
            )
        )
        bank_account = result.scalar_one_or_none()

        if not bank_account:
            return None

        return BankAccountResponse.model_validate(bank_account)

    async def create_bank_account(
        self, bank_account: BankAccountCreateRequest
    ) -> BankAccountResponse:
        """Create a bank account."""
        logger.debug("create_bank_account called")

        if bank_account.is_main:
            await self._unset_main_accounts(bank_account.user_id)

        bank_account_data = bank_account.model_dump()
        new_bank_account = BankAccount(**bank_account_data)

        self.db.add(new_bank_account)
        await self.db.commit()
        await self.db.refresh(new_bank_account)

        return BankAccountResponse.model_validate(new_bank_account)

    async def update_bank_account(
        self, bank_account_id: UUID, bank_account_data: BankAccountUpdateRequest
    ) -> BankAccountResponse:
        """Update a bank account."""
        logger.debug(f"update_bank_account called for bank_account_id={bank_account_id}")

        result = await self.db.execute(select(BankAccount).where(BankAccount.id == bank_account_id))
        bank_account = result.scalar_one_or_none()

        if not bank_account:
            raise NotFoundException("Bank account not found")

        if bank_account_data.is_main is True:
            await self._unset_main_accounts(bank_account.user_id, exclude_id=bank_account_id)

        for key, value in bank_account_data.model_dump(exclude_unset=True).items():
            setattr(bank_account, key, value)

        await self.db.commit()
        await self.db.refresh(bank_account)

        return BankAccountResponse.model_validate(bank_account)

    async def delete_bank_account(self, bank_account_id: UUID) -> None:
        """Delete a bank account."""
        logger.debug(f"delete_bank_account called for bank_account_id={bank_account_id}")
        result = await self.db.execute(select(BankAccount).where(BankAccount.id == bank_account_id))
        bank_account = result.scalar_one_or_none()

        if not bank_account:
            raise NotFoundException("Bank account not found")

        await self.db.delete(bank_account)
        await self.db.commit()

    async def _unset_main_accounts(self, user_id: UUID, exclude_id: UUID | None = None) -> None:
        """Unset all main accounts for a user."""
        logger.debug(f"_unset_main_accounts called for user_id={user_id}")
        query = select(BankAccount).where(BankAccount.user_id == user_id, BankAccount.is_main)

        if exclude_id:
            query = query.where(BankAccount.id != exclude_id)

        result = await self.db.execute(query)
        bank_accounts = result.scalars().all()

        for bank_account in bank_accounts:
            bank_account.is_main = False

        await self.db.commit()
