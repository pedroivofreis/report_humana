#!/usr/bin/env python3
"""Delete a user and all related data.

Deletes:
- Shift exchanges
- User shifts
- User timesheets
- Attachments
- Professional CRMs
- User specialties
- Institution contracts
- User absences
- User observations (received and made)
- Address
- Pix keys
- Bank accounts
- Complementary data
- User roles
- User (by soft delete or hard delete)

Usage:
  python3 scripts/delete_user.py --user-id <uuid>
  python3 scripts/delete_user.py --email user@example.com
  python3 scripts/delete_user.py --cpf 12345678901 --hard
"""

import argparse
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.api.models.address import Address
from app.api.models.attachment import Attachment
from app.api.models.bank_account import BankAccount
from app.api.models.complementary_data import ComplementaryData
from app.api.models.institution_contract import InstitutionContract
from app.api.models.institution_contract_sector_value import InstitutionContractSectorValue
from app.api.models.institutions import Institution
from app.api.models.pix_key import PixKey
from app.api.models.profession import Profession
from app.api.models.professional_crm import ProfessionalCrm
from app.api.models.role import Role
from app.api.models.sectors import Sector
from app.api.models.shift_types import ShiftType
from app.api.models.shifts import Shift, ShiftSlotConfig
from app.api.models.specialty import Specialty
from app.api.models.user import User
from app.api.models.user_absence import UserAbsence
from app.api.models.user_observation import UserObservation
from app.api.models.user_role import UserRole
from app.api.models.user_shifts import ShiftExchange, UserShift
from app.api.models.user_specialty import UserSpecialty
from app.api.models.user_timesheets import UserTimesheet
from app.db.session import AsyncSessionLocal


async def delete_user(
    user_id: str | None = None,
    email: str | None = None,
    cpf: str | None = None,
    hard_delete: bool = False,
) -> None:
    """Delete a user and all related data."""
    if not any([user_id, email, cpf]):
        raise ValueError("Must provide either user_id, email, or cpf")

    async with AsyncSessionLocal() as session:
        try:
            # Find user
            query = select(User)
            if user_id:
                query = query.where(User.id == user_id)
            elif email:
                query = query.where(User.email == email)
            elif cpf:
                query = query.where(User.cpf == cpf)

            result = await session.execute(query)
            user = result.scalar_one_or_none()

            if not user:
                raise ValueError(f"User not found with provided criteria")

            user_id_str = str(user.id)
            print(f"🔍 Found user: {user.first_name} {user.last_name} ({user.email})")
            print(f"   ID: {user_id_str}")
            print()

            # Delete in order of dependencies (leaf nodes first)
            deletion_steps = [
                ("Shift exchanges", _delete_shift_exchanges),
                ("User shifts", _delete_user_shifts),
                ("User timesheets", _delete_user_timesheets),
                ("User observations (made)", _delete_user_observations_made),
                ("User observations (received)", _delete_user_observations_received),
                ("User absences", _delete_user_absences),
                ("Professional CRMs", _delete_professional_crms),
                ("User specialties", _delete_user_specialties),
                ("Institution contracts", _delete_institution_contracts),
                ("Attachments", _delete_attachments),
                ("Address", _delete_address),
                ("Pix keys", _delete_pix_keys),
                ("Bank accounts", _delete_bank_accounts),
                ("Complementary data", _delete_complementary_data),
                ("User roles", _delete_user_roles),
            ]

            for step_name, step_func in deletion_steps:
                count = await step_func(session, user_id_str)
                if count > 0:
                    print(f"   ✅ Deleted {count} {step_name}")

            # Finally delete user
            if hard_delete:
                await session.execute(text("DELETE FROM users WHERE id = :user_id"), {"user_id": user_id_str})
                print(f"   ✅ Hard deleted user")
            else:
                # Soft delete using delete method from UserRepository
                from app.api.repositories.user import UserRepository
                user_repo = UserRepository(db=session)
                await user_repo.delete_user(user.id)
                print(f"   ✅ Soft deleted user (deleted_at set)")

            await session.commit()
            print()
            print("✅ User deletion completed successfully!")

        except Exception as e:
            await session.rollback()
            print(f"\n❌ Error during deletion: {e}")
            raise


async def _delete_shift_exchanges(session: AsyncSession, user_id: str) -> int:
    """Delete shift exchanges where user is involved."""
    # Delete exchanges where user is target
    result1 = await session.execute(
        text("DELETE FROM shift_exchanges WHERE target_user_id = :user_id"), {"user_id": user_id}
    )
    count1 = result1.rowcount

    # Delete exchanges where user is old person
    result2 = await session.execute(
        text("DELETE FROM shift_exchanges WHERE old_person_id = :user_id"), {"user_id": user_id}
    )
    count2 = result2.rowcount

    return count1 + count2


async def _delete_user_shifts(session: AsyncSession, user_id: str) -> int:
    """Delete user shifts and update timesheet references."""
    # First, unlinked shifts from their timesheets
    await session.execute(
        text("UPDATE user_shifts SET user_timesheet_id = NULL WHERE user_id = :user_id"),
        {"user_id": user_id},
    )

    # Then delete shifts
    result = await session.execute(
        text("DELETE FROM user_shifts WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_user_timesheets(session: AsyncSession, user_id: str) -> int:
    """Delete user timesheets."""
    result = await session.execute(
        text("DELETE FROM user_timesheets WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_user_observations_made(session: AsyncSession, user_id: str) -> int:
    """Delete user observations made by this user."""
    result = await session.execute(
        text("DELETE FROM user_observations WHERE owner_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_user_observations_received(session: AsyncSession, user_id: str) -> int:
    """Delete user observations for this user."""
    result = await session.execute(
        text("DELETE FROM user_observations WHERE target_user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_user_absences(session: AsyncSession, user_id: str) -> int:
    """Delete user absences."""
    result = await session.execute(
        text("DELETE FROM user_absences WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_professional_crms(session: AsyncSession, user_id: str) -> int:
    """Delete professional CRMs."""
    result = await session.execute(
        text("DELETE FROM professional_crm WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_user_specialties(session: AsyncSession, user_id: str) -> int:
    """Delete user specialties."""
    result = await session.execute(
        text("DELETE FROM user_specialties WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_institution_contracts(session: AsyncSession, user_id: str) -> int:
    """Delete institution contracts."""
    result = await session.execute(
        text("DELETE FROM institution_contracts WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_attachments(session: AsyncSession, user_id: str) -> int:
    """Delete user attachments."""
    result = await session.execute(
        text("DELETE FROM attachments WHERE entity_type = 'user' AND entity_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_address(session: AsyncSession, user_id: str) -> int:
    """Delete user address."""
    result = await session.execute(
        text("DELETE FROM addresses WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_pix_keys(session: AsyncSession, user_id: str) -> int:
    """Delete user pix keys."""
    result = await session.execute(
        text("DELETE FROM pix_keys WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_bank_accounts(session: AsyncSession, user_id: str) -> int:
    """Delete user bank accounts."""
    result = await session.execute(
        text("DELETE FROM bank_accounts WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_complementary_data(session: AsyncSession, user_id: str) -> int:
    """Delete user complementary data."""
    result = await session.execute(
        text("DELETE FROM complementary_data WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


async def _delete_user_roles(session: AsyncSession, user_id: str) -> int:
    """Delete user roles."""
    result = await session.execute(
        text("DELETE FROM users_roles WHERE user_id = :user_id"), {"user_id": user_id}
    )
    return result.rowcount


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Delete a user and all related data.")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--user-id", help="User UUID")
    group.add_argument("--email", help="User email")
    group.add_argument("--cpf", help="User CPF")
    p.add_argument(
        "--hard",
        action="store_true",
        help="Hard delete user from database (default: soft delete with deleted_at)",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    asyncio.run(
        delete_user(
            user_id=args.user_id,
            email=args.email,
            cpf=args.cpf,
            hard_delete=args.hard,
        )
    )


if __name__ == "__main__":
    main()
