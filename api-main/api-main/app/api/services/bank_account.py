"""Bank account service module."""

from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.bank_account import BankAccountRepository
from app.api.schemas.bank_account import (
    BankAccountCreateRequest,
    BankAccountResponse,
    BankAccountUpdateRequest,
)
from app.core.exceptions import NotFoundException, ResourceAlreadyExistsException

logger = structlog.getLogger(__name__)


class BankAccountService:
    """Bank account service."""

    def __init__(self, repository: BankAccountRepository = Depends(BankAccountRepository)):
        self.repository = repository

    async def get_bank_accounts(self) -> list[BankAccountResponse]:
        """Get all bank accounts."""
        logger.debug("Get all bank accounts")
        return await self.repository.get_bank_accounts()

    async def get_bank_accounts_by_user_id(self, user_id: UUID) -> list[BankAccountResponse]:
        """Get bank accounts by user id."""
        logger.debug(f"Get bank accounts by user id: {user_id}")
        return await self.repository.get_bank_accounts_by_user_id(user_id)

    async def get_main_bank_account_by_user_id(self, user_id: UUID) -> BankAccountResponse | None:
        """Get main bank account by user id."""
        logger.debug(f"Get main bank account by user id: {user_id}")
        return await self.repository.get_main_bank_account_by_user_id(user_id)

    async def get_bank_account_by_id(self, bank_account_id: UUID) -> BankAccountResponse | None:
        """Get a bank account by id."""
        logger.debug(f"Get bank account by id: {bank_account_id}")
        bank_account = await self.repository.get_bank_account_by_id(bank_account_id)
        if not bank_account:
            raise NotFoundException("Conta bancária não encontrada")

        return bank_account

    async def create_bank_account(
        self, bank_account: BankAccountCreateRequest
    ) -> BankAccountResponse:
        """Create a bank account."""
        logger.debug("Create bank account service")

        existing_account = await self.repository.get_bank_account_by_data(
            user_id=bank_account.user_id,
            bank_code=bank_account.bank_code,
            agency=bank_account.agency,
            account_number=bank_account.account_number,
            account_digit=bank_account.account_digit,
            account_type=bank_account.account_type,
        )

        if existing_account:
            raise ResourceAlreadyExistsException(resource_name="Conta bancária")

        return await self.repository.create_bank_account(bank_account)

    async def update_bank_account(
        self, bank_account_id: UUID, bank_account: BankAccountUpdateRequest
    ) -> BankAccountResponse:
        """Update a bank account."""
        logger.debug(f"Update bank account by id: {bank_account_id}")

        if await self.repository.get_bank_account_by_id(bank_account_id) is None:
            raise NotFoundException("Conta bancária não encontrada")

        return await self.repository.update_bank_account(bank_account_id, bank_account)

    async def delete_bank_account(self, bank_account_id: UUID) -> None:
        """Delete a bank account."""
        logger.debug(f"Delete bank account by id: {bank_account_id}")

        if await self.repository.get_bank_account_by_id(bank_account_id) is None:
            raise NotFoundException("Conta bancária não encontrada")

        return await self.repository.delete_bank_account(bank_account_id)
