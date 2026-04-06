from datetime import datetime
from typing import Any
from uuid import UUID

import pydantic


class SectorResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    description: str | None = None
    is_active: bool = True
    institution_id: UUID | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    # Internal relationship to compute current value
    contract_values: list[Any] = pydantic.Field(default=[], exclude=True)

    @pydantic.computed_field
    @property
    def current_contract_value(self) -> float | None:
        """Returns the active hourly contract value based on current date."""
        from datetime import date

        today = date.today()

        try:
            values = list(self.contract_values)
        except Exception:
            return None

        # Sort values by start_date descending (newest first)
        active_values = []
        for val in values:
            start_date = getattr(val, "start_date", None)
            end_date = getattr(val, "end_date", None)

            if not start_date:
                continue

            if start_date <= today and (not end_date or end_date >= today):
                active_values.append(val)

        if not active_values:
            return None

        # Get the one with the most recent start date
        active_values.sort(key=lambda x: getattr(x, "start_date", date.min), reverse=True)
        return getattr(active_values[0], "hourly_value", None)


class SectorRequest(pydantic.BaseModel):
    display_name: str
    description: str | None = None
    is_active: bool = True
    institution_id: UUID | None = None
