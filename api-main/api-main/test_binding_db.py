import asyncio
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionLocal
from app.api.models.user import User
from app.api.models.address import Address
from app.api.models.bank_account import BankAccount
from app.api.models.complementary_data import ComplementaryData
from app.api.models.institution_contract import InstitutionContract
from app.api.models.pix_key import PixKey
from app.api.models.profession import Profession
from app.api.models.professional_crm import ProfessionalCrm
from app.api.models.user_absence import UserAbsence
from app.api.models.user_observation import UserObservation
from app.api.models.user_role import UserRole
from app.api.models.user_specialty import UserSpecialty
from app.api.models.professional_location_binding import ProfessionalLocationBinding
from app.api.models.professional_location_sector import ProfessionalLocationSector
from app.api.models.sectors import Sector
from app.api.models.institutions import Institution
from app.api.models.institution_contract_sector_value import InstitutionContractSectorValue
from app.api.models.institution_contract import InstitutionContract
from app.api.models.role import Role
from app.api.models.specialty import Specialty
from app.api.models.professional_location_binding import BindingContractType, BindingStatus

async def test_binding():
    async with AsyncSessionLocal() as session:
        # 1. Create a mock user
        user = User(
            id=uuid4(),
            first_name="Test",
            last_name="Professional",
            email=f"test{uuid4()}@example.com",
            cpf="66464405063", # simplified
        )
        session.add(user)
        
        # 2. Create a mock institution
        inst = Institution(
            id=uuid4(),
            display_name="Test Hospital",
            social_name="Test Hospital LTDA",
            tax_document="86266052000120",
        )
        session.add(inst)
        
        # 3. Create mock sectors
        sector1 = Sector(id=uuid4(), display_name="Cardiology", institution_id=inst.id)
        sector2 = Sector(id=uuid4(), display_name="Neurology", institution_id=inst.id)
        session.add(sector1)
        session.add(sector2)
        
        await session.flush()
        
        print(f"Created User: {user.id}")
        print(f"Created Institution: {inst.id}")
        print(f"Created Sectors: {sector1.id}, {sector2.id}")
        
        # 4. Create a binding
        binding = ProfessionalLocationBinding(
            user_id=user.id,
            institution_id=inst.id,
            contract_type=BindingContractType.CLT,
            status=BindingStatus.PENDING,
        )
        session.add(binding)
        await session.flush()
        
        # 5. Link sectors
        link1 = ProfessionalLocationSector(binding_id=binding.id, sector_id=sector1.id)
        link2 = ProfessionalLocationSector(binding_id=binding.id, sector_id=sector2.id)
        session.add(link1)
        session.add(link2)
        
        await session.commit()
        
        # 6. Verify retrieval
        stmt = (
            select(ProfessionalLocationBinding)
            .where(ProfessionalLocationBinding.id == binding.id)
            .options(
                selectinload(ProfessionalLocationBinding.sectors).selectinload(ProfessionalLocationSector.sector)
            )
        )
        res = await session.execute(stmt)
        saved_binding = res.scalars().first()
        
        print("\n--- Test Results ---")
        print(f"Binding ID: {saved_binding.id}")
        print(f"Contract: {saved_binding.contract_type.value} Status: {saved_binding.status.value}")
        print(f"Sectors linked: {len(saved_binding.sectors)}")
        for i, s in enumerate(saved_binding.sectors):
            print(f" Sector {i+1}: {s.sector.display_name} (ID: {s.sector.id})")
        print("Integration Test Successful!")

if __name__ == "__main__":
    asyncio.run(test_binding())
