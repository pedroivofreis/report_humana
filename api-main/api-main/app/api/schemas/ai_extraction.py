"""AI Extraction schemas module."""

from pydantic import BaseModel, ConfigDict, Field


class TimesheetImageData(BaseModel):
    """Schema for data extracted from timesheet image by Gemini."""

    model_config = ConfigDict(populate_by_name=True)

    parent_institution_name: str | None = Field(None, alias="parent_institutions.display_name")
    child_institution_name: str | None = Field(None, alias="child_institutions.display_name")

    user_first_name: str | None = Field(None, alias="user.first_name")
    user_last_name: str | None = Field(None, alias="user.last_name")
    user_crm: str | None = Field(None, alias="user.crm")

    date_day: str | None = Field(None, alias="Data_Dia")
    start_time_1: str | None = Field(None, alias="Entrada_1")
    end_time_1: str | None = Field(None, alias="Saida_1")
    start_time_2: str | None = Field(None, alias="Entrada_2")
    end_time_2: str | None = Field(None, alias="Saida_2")

    has_signature: bool | str | None = Field(None, alias="Carimbo_Assinatura")
