import asyncio
import uuid

from app.api.repositories.bank_account import BankAccountRepository
from app.api.schemas.bank_account import BankAccountCreateRequest
from app.api.services.bank_account import BankAccountService
from app.core.exceptions import ResourceAlreadyExistsException
from app.db.session import AsyncSessionLocal


async def verify_duplicate_check():
    async with AsyncSessionLocal() as session:
        repo = BankAccountRepository(db=session)
        service = BankAccountService(repository=repo)

        user_id = uuid.uuid4()
        bank_data = {
            "user_id": user_id,
            "bank_code": "001",
            "bank_name": "Test Bank",
            "agency": "1234",
            "account_number": "56789",
            "account_digit": "0",
            "account_type": "checking",
            "is_main": True,
        }

        request = BankAccountCreateRequest(**bank_data)

        print("Creating first account...")
        try:
            created = await service.create_bank_account(request)
            print(f"Created account: {created.id}")
        except Exception as e:
            print(f"Failed to create first account: {e}")
            return

        print("Creating duplicate account...")
        try:
            await service.create_bank_account(request)
            print("ERROR: Duplicate account created!")
        except ResourceAlreadyExistsException:
            print("SUCCESS: Duplicate account blocked.")
        except Exception as e:
            print(f"ERROR: Unexpected exception: {e}")

        # Cleanup (optional if using test DB, but safe to delete what we created)
        print("Cleaning up...")
        await repo.delete_bank_account(created.id)
        print("Cleanup done.")


if __name__ == "__main__":
    asyncio.run(verify_duplicate_check())
