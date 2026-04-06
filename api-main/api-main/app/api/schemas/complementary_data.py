"""Complementary data schema module."""

from datetime import datetime
from enum import Enum
from uuid import UUID

import pydantic


class MaritalStatusEnum(str, Enum):
    """Marital status enum."""

    SINGLE = "SINGLE"
    MARRIED = "MARRIED"
    DIVORCED = "DIVORCED"
    WIDOWED = "WIDOWED"
    DOMESTIC_PARTNERSHIP = "DOMESTIC_PARTNERSHIP"


class GenderEnum(str, Enum):
    """Gender enum."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    NON_BINARY = "NON_BINARY"
    TRANSGENDER = "TRANSGENDER"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class RaceEnum(str, Enum):
    """Race enum."""

    WHITE = "WHITE"
    BLACK = "BLACK"
    BROWN = "BROWN"
    ASIAN = "ASIAN"
    INDIGENOUS = "INDIGENOUS"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class ComplementaryDataResponse(pydantic.BaseModel):
    """Complementary data response schema."""

    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    marital_status: MaritalStatusEnum | None = None
    place_of_birth: str | None = None
    nationality: str | None = None
    mother_name: str | None = None
    father_name: str | None = None
    has_disability: bool | None = None
    disability: str | None = None
    gender: GenderEnum | None = None
    race: RaceEnum | None = None
    created_at: datetime
    updated_at: datetime | None = None


class ComplementaryDataCreateRequest(pydantic.BaseModel):
    """Complementary data create request schema."""

    marital_status: MaritalStatusEnum | None = None
    place_of_birth: str | None = None
    nationality: str | None = None
    mother_name: str | None = None
    father_name: str | None = None
    has_disability: bool | None = None
    disability: str | None = None
    gender: GenderEnum | None = None
    race: RaceEnum | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, values: dict) -> dict:
        """Converte strings vazias em None para campos opcionais."""
        enum_fields = {"marital_status", "gender", "race", "sex", "disability",
                       "place_of_birth", "nationality", "mother_name", "father_name"}
        return {
            k: (None if isinstance(v, str) and not v.strip() and k in enum_fields else v)
            for k, v in values.items()
        }

    @pydantic.field_validator("disability")
    @classmethod
    def validate_disability(cls, v: str | None, info: pydantic.ValidationInfo) -> str | None:
        """Validate disability field."""
        has_disability = info.data.get("has_disability")
        if has_disability is True and not v:
            raise ValueError("disability is required when has_disability is True")
        return v


class ComplementaryDataUpdateRequest(pydantic.BaseModel):
    """Complementary data update request schema."""

    marital_status: MaritalStatusEnum | None = None
    place_of_birth: str | None = None
    nationality: str | None = None
    mother_name: str | None = None
    father_name: str | None = None
    has_disability: bool | None = None
    disability: str | None = None
    gender: GenderEnum | None = None
    race: RaceEnum | None = None

    @pydantic.model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, values: dict) -> dict:
        """Converte strings vazias em None para campos opcionais."""
        enum_fields = {"marital_status", "gender", "race", "sex", "disability",
                       "place_of_birth", "nationality", "mother_name", "father_name"}
        return {
            k: (None if isinstance(v, str) and not v.strip() and k in enum_fields else v)
            for k, v in values.items()
        }

    @pydantic.field_validator("disability")
    @classmethod
    def validate_disability(cls, v: str | None, info: pydantic.ValidationInfo) -> str | None:
        """Validate disability field."""
        has_disability = info.data.get("has_disability")
        if has_disability is True and not v:
            raise ValueError("disability is required when has_disability is True")
        return v
