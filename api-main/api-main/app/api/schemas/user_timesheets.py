"""User Timesheet schemas module."""

from datetime import datetime
from uuid import UUID

import pydantic
from pydantic import BaseModel

from app.api.models.user_timesheets import TimesheetStatus
from app.api.schemas.user import UserSimpleResponse
from app.api.schemas.user_shifts import UserShiftResponse


class UserTimesheetBase(BaseModel):
    competence_date: str
    status: TimesheetStatus
    notes: str | None = None


class UserTimesheetCreate(UserTimesheetBase):
    user_id: UUID
    institution_id: UUID
    sector_id: UUID


class UserTimesheetUpdate(BaseModel):
    status: TimesheetStatus | None = None
    notes: str | None = None
    closed_at: datetime | None = None


class UserTimesheetStatusUpdate(BaseModel):
    status: TimesheetStatus = pydantic.Field(..., description="Novo status do timesheet")
    rejection_reason: str | None = pydantic.Field(
        None, description="Motivo da reprovação (obrigatório se reprovado)"
    )


class UserTimesheetResponse(UserTimesheetBase):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    institution_id: UUID
    sector_id: UUID
    total_hours_planned: float
    total_hours_realized: float
    total_value_planned: float
    total_value_payable: float
    total_value_payable: float  # type: ignore[no-redef]
    closed_at: datetime | None
    url: str | None = None

    shifts: list[UserShiftResponse] = []


class SectorResponse(BaseModel):
    """Sector response with basic information."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    description: str | None = None


class InstitutionResponse(BaseModel):
    """Institution response with basic information."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    social_name: str


class UserTimesheetDetailResponse(UserTimesheetBase):
    """Enhanced timesheet response with professional, sector, institution and user-shifts data."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    institution_id: UUID
    sector_id: UUID
    total_hours_planned: float
    total_hours_realized: float
    total_value_planned: float
    total_value_payable: float
    total_value_payable: float  # type: ignore[no-redef]
    closed_at: datetime | None
    url: str | None = None

    # Related data
    user: UserSimpleResponse | None = None
    sector: SectorResponse | None = None
    institution: InstitutionResponse | None = None
    shifts: list[UserShiftResponse] = []

    user_crm: str | None = None

    @pydantic.computed_field
    @property
    def assigned_to(self) -> str:
        """Returns user's full name or 'Não atribuído' if no user assigned."""
        if self.user:
            return f"{self.user.first_name} {self.user.last_name}"
        return "Não atribuído"

    @pydantic.model_validator(mode="before")
    @classmethod
    def extract_crm(cls, data: object) -> object:
        """Extract CRM from user documents if available."""
        # Use getattr to safely access attributes
        user = getattr(data, "user", None)
        if user and hasattr(user, "professional_crms") and getattr(user, "professional_crms"):
            crm_code = getattr(user.professional_crms[0], "code", None)
            if crm_code:
                if not isinstance(data, dict):
                    try:
                        object.__setattr__(data, "user_crm", crm_code)
                    except (AttributeError, TypeError):
                        pass
                else:
                    data["user_crm"] = crm_code
        return data


class ShiftsSummaryByUserSectorResponse(BaseModel):
    """Flat summary of shifts by user and sector."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    competence_date: str
    user_id: UUID | None = None
    user_name: str  # "Sem Responsável" if null
    user_crm: str | None = None

    sector_id: UUID
    sector_name: str
    institution_id: UUID
    institution_name: str

    # Timesheet info
    timesheet_id: UUID | None = None
    timesheet_status: str | None = None

    # Counts and values
    planned_count: int
    planned_value: float
    accomplished_count: int
    accomplished_value: float
    pending_count: int

    shifts_summary: str  # e.g., "2/4" = accomplished/planned
    total_value: float


class ShiftsBySectorGroupResponse(BaseModel):
    """Shifts grouped by sector with totals."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    sector: SectorResponse
    institution: InstitutionResponse
    total_shifts: int
    total_value: float
    shifts: list[UserShiftResponse] = []


class UserShiftsGroup(BaseModel):
    """User shifts group with totals."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    user: UserSimpleResponse | None = None
    assigned_to: str
    total_shifts: int
    total_value: float
    shifts: list[UserShiftResponse] = []


class SectorWithUsersGroupResponse(BaseModel):
    """Sector with users and their shifts."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    sector: SectorResponse
    institution: InstitutionResponse
    users: list[UserShiftsGroup] = []
