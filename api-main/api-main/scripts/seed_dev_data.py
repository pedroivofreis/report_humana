#!/usr/bin/env python3
"""Seed development database with initial data.

Creates:
- 1 admin user
- 1 professional user
- 1 institution with sectors

Usage:
  python scripts/seed_dev_data.py
"""

import asyncio
from pathlib import Path

import uuid  # noqa: E402

import uuid_utils  # noqa: E402

# Monkeypatch uuid7 to return standard UUID to satisfy SQLAlchemy's strict typing checks
# during bulk inserts (sentinel matching).
_original_uuid7 = uuid_utils.uuid7


def _compatible_uuid7() -> uuid.UUID:
    return uuid.UUID(int=_original_uuid7().int)


uuid_utils.uuid7 = _compatible_uuid7

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to path
sys_path = str(Path(__file__).resolve().parent.parent)
import sys

if sys_path not in sys.path:
    sys.path.insert(0, sys_path)

from app.api.models.address import Address
from app.api.models.complementary_data import ComplementaryData
from app.api.models.institution_contract import InstitutionContract
from app.api.models.institution_contract_sector_value import InstitutionContractSectorValue
from app.api.models.institutions import Institution
from app.api.models.profession import Profession
from app.api.models.professional_location_binding import (
    ProfessionalLocationBinding,
    BindingContractType,
    BindingStatus,
)
from app.api.models.professional_location_sector import ProfessionalLocationSector
from app.api.models.role import Role
from app.api.models.sectors import Sector
from app.api.models.specialty import Specialty
from app.api.models.user import User, UserStatus
from app.api.models.user_specialty import UserSpecialty
from app.api.models.user_role import UserRole
from app.api.models.bank_account import BankAccount
from app.api.models.pix_key import PixKey
from app.api.models.user_absence import UserAbsence
from app.api.models.professional_crm import ProfessionalCrm
from app.api.models.user_observation import UserObservation
from app.api.schemas.complementary_data import GenderEnum, MaritalStatusEnum, RaceEnum
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal


def _generate_valid_cpf(seq: int) -> str:
    """Generate a valid CPF from a sequence number."""
    base = f"{seq:09d}"

    sum1 = sum(int(base[i]) * (10 - i) for i in range(9))
    digit1 = (sum1 * 10) % 11
    if digit1 == 10:
        digit1 = 0

    base_with_digit1 = base + str(digit1)
    sum2 = sum(int(base_with_digit1[i]) * (11 - i) for i in range(10))
    digit2 = (sum2 * 10) % 11
    if digit2 == 10:
        digit2 = 0

    return base + str(digit1) + str(digit2)


def _generate_valid_cnpj(base: str) -> str:
    """Generate a valid CNPJ from a base number (12 digits)."""
    base = base.zfill(12)

    # First verification digit
    weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_val = sum(int(base[i]) * weights1[i] for i in range(12))
    remainder = sum_val % 11
    if remainder < 2:
        digit1 = 0
    else:
        digit1 = 11 - remainder

    base_with_digit1 = base + str(digit1)

    # Second verification digit
    weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    sum_val = sum(int(base_with_digit1[i]) * weights2[i] for i in range(13))
    remainder = sum_val % 11
    if remainder < 2:
        digit2 = 0
    else:
        digit2 = 11 - remainder

    return base + str(digit1) + str(digit2)


async def seed_admin_user(session: AsyncSession) -> User:
    """Create admin user if doesn't exist."""
    email = "admin@humana.com"

    existing = await session.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        print("ℹ️  Admin user already exists")
        existing_user = (await session.execute(select(User).where(User.email == email))).scalar_one()
        return existing_user

    # Generate valid CPF
    cpf = _generate_valid_cpf(123456789)

    admin_user = User(
        first_name="Admin",
        last_name="System",
        is_active=True,
        status=UserStatus.ACTIVE,
        cpf="09944055026",
        email=email,
        phone="11999999999",
        password=get_password_hash("Admin123!"),
    )
    session.add(admin_user)
    await session.flush()

    # Add admin role
    admin_role = await session.execute(select(Role).where(Role.name == "admin"))
    admin_role = admin_role.scalar_one_or_none()
    if admin_role:
        session.add(UserRole(user_id=admin_user.id, role_id=admin_role.id))

    # Add address
    session.add(
        Address(
            user_id=admin_user.id,
            zip_code="01310000",
            street="Av. Paulista",
            number="1000",
            complement="Sala 100",
            neighborhood="Bela Vista",
            city="São Paulo",
            uf="SP",
        )
    )

    await session.flush()
    print(f"✅ Admin user created: {email}")
    print(f"   CPF: {cpf}")
    return admin_user


async def seed_professional_user(session: AsyncSession) -> User:
    """Create professional user if doesn't exist."""
    email = "professional@humana.com"

    existing = await session.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        print("ℹ️  Professional user already exists")
        existing_user = (await session.execute(select(User).where(User.email == email))).scalar_one()
        return existing_user

    # Generate valid CPF
    cpf = _generate_valid_cpf(987654321)

    prof_user = User(
        first_name="João",
        last_name="Silva",
        is_active=True,
        status=UserStatus.ACTIVE,
        cpf=cpf,
        email=email,
        phone="11988887777",
        password=get_password_hash("Professional123!"),
    )
    session.add(prof_user)
    await session.flush()

    # Add professional role
    prof_role = await session.execute(select(Role).where(Role.name == "professional"))
    prof_role = prof_role.scalar_one_or_none()
    if prof_role:
        session.add(UserRole(user_id=prof_user.id, role_id=prof_role.id))

    # Add address
    session.add(
        Address(
            user_id=prof_user.id,
            zip_code="04538000",
            street="Av. Santo Amaro",
            number="5000",
            complement=None,
            neighborhood="Indianópolis",
            city="São Paulo",
            uf="SP",
        )
    )

    # Add complementary data
    session.add(
        ComplementaryData(
            user_id=prof_user.id,
            marital_status=MaritalStatusEnum.SINGLE,
            place_of_birth="São Paulo",
            nationality="BR",
            mother_name="Maria Silva",
            father_name="José Silva",
            has_disability=False,
            gender=GenderEnum.MALE,
            race=RaceEnum.WHITE,
        )
    )

    # Add profession (Medicina)
    prof = await session.execute(select(Profession).where(Profession.name == "Medicina"))
    prof = prof.scalar_one_or_none()
    if prof:
        prof_user.profession_id = prof.id

        # Add specialty (Cardiologia)
        spec = await session.execute(
            select(Specialty).where(Specialty.name == "Cardiologia")
        )
        spec = spec.scalar_one_or_none()
        if spec:
            session.add(
                UserSpecialty(
                    user_id=prof_user.id,
                    specialty_id=spec.id,
                    is_primary=True,
                )
            )

    await session.flush()
    print(f"✅ Professional user created: {email}")
    print(f"   CPF: {cpf}")
    return prof_user


async def seed_institution_with_sectors(session: AsyncSession) -> tuple[Institution, list[Sector]]:
    """Create institution with sectors if doesn't exist."""
    # Generate valid CNPJ: 12.345.678/0001-XX
    cnpj = _generate_valid_cnpj("123456780001")

    existing = await session.execute(select(Institution).where(Institution.tax_document == cnpj))
    if existing.scalar_one_or_none():
        print("ℹ️  Institution already exists")
        institution = (await session.execute(select(Institution).where(Institution.tax_document == cnpj))).scalar_one()
        sectors = await session.execute(select(Sector).where(Sector.institution_id == institution.id))
        return institution, list(sectors.scalars().all())

    institution = Institution(
        display_name="Hospital Humana",
        social_name="Hospital Humana LTDA",
        tax_document=cnpj,
        is_active=True,
    )
    session.add(institution)
    await session.flush()

    # Add sectors
    sectors_data = [
        {"name": "Clínica Médica", "description": "Clínica geral"},
        {"name": "Cardiologia", "description": "Setor de cardiologia"},
        {"name": "Pediatria", "description": "Setor pediátrico"},
        {"name": "UTI Adulto", "description": "Unidade de Terapia Intensiva"},
        {"name": "UTI Pediátrica", "description": "UTI pediátrica"},
        {"name": "Emergência", "description": "Pronto-socorro"},
        {"name": "Cirurgia", "description": "Centro cirúrgico"},
        {"name": "Radiologia", "description": "Imagens diagnósticas"},
    ]

    created_sectors = []
    for sector_data in sectors_data:
        sector = Sector(
            display_name=sector_data["name"],
            description=sector_data["description"],
            is_active=True,
            institution_id=institution.id,
        )
        session.add(sector)
        created_sectors.append(sector)

    await session.flush()
    print(f"✅ Institution created: {institution.display_name}")
    print(f"   CNPJ: {cnpj}")
    print(f"   - {len(created_sectors)} sectors created")
    return institution, created_sectors


async def seed_professional_binding(session: AsyncSession, user: User, institution: Institution, sectors: list[Sector]) -> None:
    """Create professional-location binding if doesn't exist."""
    existing = await session.execute(
        select(ProfessionalLocationBinding).where(
            ProfessionalLocationBinding.user_id == user.id,
            ProfessionalLocationBinding.institution_id == institution.id,
        )
    )
    if existing.scalar_one_or_none():
        print("ℹ️  Professional binding already exists")
        return

    binding = ProfessionalLocationBinding(
        user_id=user.id,
        institution_id=institution.id,
        contract_type=BindingContractType.CLT,
        status=BindingStatus.ACTIVE,
    )
    session.add(binding)
    await session.flush()

    # Add sectors to binding (Cardiologia + Clínica Médica)
    card_sector = next((s for s in sectors if "Cardiologia" in s.display_name), None)
    clin_sector = next((s for s in sectors if "Clínica Médica" in s.display_name), None)

    for sector in [card_sector, clin_sector]:
        if sector:
            session.add(
                ProfessionalLocationSector(
                    binding_id=binding.id,
                    sector_id=sector.id,
                )
            )

    await session.flush()
    print(f"✅ Professional binding created for {user.email} at {institution.display_name}")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        # Seed users
        admin_user = await seed_admin_user(session)
        prof_user = await seed_professional_user(session)

        # Seed institution with sectors
        institution, sectors = await seed_institution_with_sectors(session)

        # Create binding between professional user and institution
        await seed_professional_binding(session, prof_user, institution, sectors)

        await session.commit()

    print("\n" + "=" * 50)
    print("✅ Seed de desenvolvimento concluído!")
    print("=" * 50)
    print("\n📧 Usuários criados:")
    print("   Admin: cpf 09944055026 | email: admin@humana.com | Senha: password")
    print("   Profissional: email: professional@humana.com | Senha: password")
    print(f"\n🏥 Instituição: {institution.display_name}")


if __name__ == "__main__":
    asyncio.run(main())
