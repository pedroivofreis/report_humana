"""Database base module."""

from app.api.models.address import Address  # noqa: F401
from app.api.models.attachment import Attachment  # noqa: F401
from app.api.models.bank_account import BankAccount  # noqa: F401
from app.api.models.complementary_data import ComplementaryData  # noqa: F401
from app.api.models.institution_contract import InstitutionContract  # noqa: F401
from app.api.models.institution_contract_sector_value import (  # noqa: F401
    InstitutionContractSectorValue,
)
from app.api.models.institutions import Institution
from app.api.models.pix_key import PixKey  # noqa: F401
from app.api.models.profession import Profession  # noqa: F401
from app.api.models.professional_crm import ProfessionalCrm  # noqa: F401
from app.api.models.professional_location_binding import ProfessionalLocationBinding  # noqa: F401
from app.api.models.professional_location_sector import ProfessionalLocationSector  # noqa: F401
from app.api.models.role import Role  # noqa: F401
from app.api.models.sectors import Sector
from app.api.models.shift_types import ShiftType  # noqa: F401
from app.api.models.shifts import Shift, ShiftSlotConfig  # noqa: F401
from app.api.models.specialty import Specialty  # noqa: F401
from app.api.models.user import User  # noqa: F401
from app.api.models.user_absence import UserAbsence  # noqa: F401
from app.api.models.user_observation import UserObservation  # noqa: F401
from app.api.models.user_role import UserRole  # noqa: F401
from app.api.models.user_shifts import UserShift  # noqa: F401
from app.api.models.user_specialty import UserSpecialty  # noqa: F401
from app.api.models.user_timesheets import UserTimesheet  # noqa: F401
from app.db.session import Base

__all__ = [
    "Base",
    "Address",
    "Attachment",
    "BankAccount",
    "ComplementaryData",
    "PixKey",
    "Profession",
    "ProfessionalCrm",
    "InstitutionContract",
    "InstitutionContractSectorValue",
    "Role",
    "Specialty",
    "User",
    "UserRole",
    "UserSpecialty",
    "Institution",
    "ProfessionalLocationBinding",
    "ProfessionalLocationSector",
    "Sector",
    "Shift",
    "ShiftSlotConfig",
    "UserShift",
    "UserTimesheet",
    "ShiftType",
    "UserAbsence",
    "UserObservation",
]
