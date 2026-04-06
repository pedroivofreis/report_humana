"""Bank account router module."""

from uuid import UUID

import fastapi
import structlog
from fastapi import Depends

from app.api.schemas.bank_account import (
    BankAccountCreateRequest,
    BankAccountResponse,
    BankAccountUpdateRequest,
)
from app.api.services.bank_account import BankAccountService

logger = structlog.get_logger(__name__)

router = fastapi.APIRouter()


@router.get(
    "",
    response_model=list[BankAccountResponse],
    status_code=200,
    description="Bank account endpoint to get all bank accounts",
)
async def bank_accounts(
    service: BankAccountService = Depends(BankAccountService),
) -> list[BankAccountResponse]:
    """
    Bank account endpoint to get all bank accounts.

    Args:
        service: Bank account service dependency.

    Returns:
        list[BankAccountResponse]: List of bank accounts.
    """
    logger.info("Getting all bank accounts")
    return await service.get_bank_accounts()


@router.get(
    "/user/{user_id}",
    response_model=list[BankAccountResponse],
    status_code=200,
    description="Bank account endpoint to get bank accounts by user id",
)
async def bank_accounts_by_user_id(
    user_id: UUID,
    service: BankAccountService = Depends(BankAccountService),
) -> list[BankAccountResponse]:
    """
    Bank account endpoint to get bank accounts by user id.

    Args:
        user_id: User id.
        service: Bank account service dependency.

    Returns:
        list[BankAccountResponse]: List of bank accounts.
    """
    logger.info("Getting bank accounts by user id")
    logger.info(f"User id: {user_id}")
    return await service.get_bank_accounts_by_user_id(user_id)


@router.get(
    "/user/{user_id}/main",
    response_model=BankAccountResponse | None,
    status_code=200,
    description="Bank account endpoint to get main bank account by user id",
)
async def main_bank_account_by_user_id(
    user_id: UUID,
    service: BankAccountService = Depends(BankAccountService),
) -> BankAccountResponse | None:
    """
    Bank account endpoint to get main bank account by user id.

    Args:
        user_id: User id.
        service: Bank account service dependency.

    Returns:
        BankAccountResponse | None: Main bank account or None.
    """
    logger.info("Getting main bank account by user id")
    logger.info(f"User id: {user_id}")
    return await service.get_main_bank_account_by_user_id(user_id)


@router.get(
    "/{bank_account_id}",
    response_model=BankAccountResponse,
    status_code=200,
    description="Bank account endpoint to get a bank account by id.",
)
async def bank_account_by_id(
    bank_account_id: UUID,
    service: BankAccountService = Depends(BankAccountService),
) -> BankAccountResponse | None:
    """
    Bank account endpoint to get a bank account by id.

    Args:
        bank_account_id: Bank account id.
        service: Bank account service dependency.

    Returns:
        BankAccountResponse: Bank account.
    """
    logger.info("Getting bank account by id")
    logger.info(f"Bank account id: {bank_account_id}")
    return await service.get_bank_account_by_id(bank_account_id)


@router.post(
    "",
    response_model=BankAccountResponse,
    status_code=201,
    description="Bank account endpoint to create a bank account.",
)
async def create_bank_account(
    bank_account: BankAccountCreateRequest,
    service: BankAccountService = Depends(BankAccountService),
) -> BankAccountResponse:
    """
    Bank account endpoint to create a bank account.

    Args:
        bank_account: Bank account data.
        service: Bank account service dependency.

    Returns:
        BankAccountResponse: Bank account.
    """
    logger.info("Creating bank account")
    logger.info(f"Bank account: {bank_account}")
    return await service.create_bank_account(bank_account)


@router.put(
    "/{bank_account_id}",
    response_model=BankAccountResponse,
    status_code=200,
    description="Bank account endpoint to update a bank account.",
)
async def update_bank_account(
    bank_account_id: UUID,
    bank_account: BankAccountUpdateRequest,
    service: BankAccountService = Depends(BankAccountService),
) -> BankAccountResponse:
    """
    Bank account endpoint to update a bank account.

    Args:
        bank_account_id: Bank account id.
        bank_account: Bank account data.
        service: Bank account service dependency.

    Returns:
        BankAccountResponse: Bank account.
    """
    logger.info("Updating bank account")
    logger.info(f"Bank account id: {bank_account_id}")
    logger.info(f"Bank account: {bank_account}")
    return await service.update_bank_account(bank_account_id, bank_account)


@router.delete(
    "/{bank_account_id}",
    status_code=204,
    description="Bank account endpoint to delete a bank account.",
)
async def delete_bank_account(
    bank_account_id: UUID,
    service: BankAccountService = Depends(BankAccountService),
) -> None:
    """
    Bank account endpoint to delete a bank account.

    Args:
        bank_account_id: Bank account id.
        service: Bank account service dependency.

    Returns:
        None.
    """
    logger.info("Deleting bank account")
    logger.info(f"Bank account id: {bank_account_id}")
    return await service.delete_bank_account(bank_account_id)
