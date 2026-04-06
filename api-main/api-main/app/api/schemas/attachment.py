"""Attachment schema module."""

from datetime import datetime
from typing import Any
from uuid import UUID

import pydantic
from fastapi import File, Form, UploadFile


class AttachmentResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    entity_id: UUID
    entity_type: str
    title: str
    description: str | None = None
    url: str | None = None
    file_key: str | None = pydantic.Field(default=None, exclude=True)
    created_at: datetime
    updated_at: datetime | None = None


class AttachmentCreateRequest(pydantic.BaseModel):
    entity_id: UUID = pydantic.Field(..., description="Entity ID")
    entity_type: str = pydantic.Field(..., description="Entity Type")
    title: str = pydantic.Field(..., min_length=1, max_length=255, description="Attachment title")
    description: str | None = pydantic.Field(None, description="Attachment description")

    @pydantic.field_validator("entity_id", mode="before")
    @classmethod
    def _normalize_entity_id(cls, v: Any) -> Any:
        if v is None:
            return v
        if isinstance(v, str):
            s = v.strip()
            s = s.strip('"').strip("'").strip()
            return s
        return v


class AttachmentCreateRequestForm(AttachmentCreateRequest):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    entity_id: UUID
    entity_type: str
    title: str
    description: str | None = None
    file: UploadFile | None = None

    @pydantic.field_validator("title", mode="before")
    @classmethod
    def _empty_string_to_none_str_fields(cls, v: Any) -> Any:
        if v == "":
            raise ValueError("Title cannot be empty")
        return v

    @classmethod
    def as_form(
        cls,
        entity_id: UUID = Form(...),
        entity_type: str = Form(...),
        title: str = Form(...),
        description: str | None = Form(None),
        file: UploadFile | None = File(None),
    ) -> "AttachmentCreateRequestForm":
        return cls(
            entity_id=entity_id,
            entity_type=entity_type,
            title=title,
            description=description,
            file=file,
        )


class AttachmentUpdateRequest(pydantic.BaseModel):
    title: str | None = pydantic.Field(
        None, min_length=1, max_length=255, description="Attachment title"
    )
    description: str | None = pydantic.Field(
        None, description="Attachment description"
    )
