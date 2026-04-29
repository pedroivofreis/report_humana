"""User schema module."""

from datetime import date, datetime
from typing import Any
from uuid import UUID

import pydantic
from fastapi import File, Form, UploadFile

from app.api.models.user import UserStatus
from app.api.schemas.address import AddressResponse
from app.api.schemas.attachment import AttachmentResponse
from app.api.schemas.bank_account import BankAccountResponse
from app.api.schemas.complementary_data import ComplementaryDataResponse
from app.api.schemas.pix_key import PixKeyResponse
from app.api.schemas.profession import ProfessionResponse
from app.api.schemas.role import RoleResponse
from app.api.schemas.user_specialty import (
    UserSpecialtyCreateForUserRequest,
    UserSpecialtyWithDetailsResponse,
)
from app.core.cpf import Cpf
from app.core.phone import Phone


class PaginatedResponse(pydantic.BaseModel):
    """Paginated response model."""

    total: int
    page: int
    page_size: int
    total_pages: int


class UserResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    is_active: bool
    status: UserStatus
    cpf: Cpf
    email: str
    phone: Phone | None = None
    profile_picture: str | None = None
    date_of_birth: date | None = None
    profession: ProfessionResponse | None = None
    created_at: datetime
    updated_at: datetime | None = None
    roles: list[RoleResponse] = []
    user_specialties: list[UserSpecialtyWithDetailsResponse] = []


class UserSimpleResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    status: UserStatus


class UserRegisterStatusResponse(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)

    user_id: UUID
    status: UserStatus
    is_active: bool


class UserResponseById(UserResponse):
    model_config = pydantic.ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    last_name: str
    is_active: bool
    cpf: Cpf
    email: str
    phone: Phone | None = None
    profile_picture: str | None = None
    date_of_birth: date | None = None
    profession: ProfessionResponse | None = None
    created_at: datetime
    updated_at: datetime | None = None
    roles: list[RoleResponse] = []
    complementary_data: ComplementaryDataResponse | None = None
    address: AddressResponse | None = None
    bank_accounts: list[BankAccountResponse] = []
    user_specialties: list[UserSpecialtyWithDetailsResponse] = []
    pix_keys: list[PixKeyResponse] = []
    attachments: list[AttachmentResponse] = []


class UserCreateRequest(pydantic.BaseModel):
    first_name: str
    last_name: str
    cpf: str
    password: str | None = None
    email: str
    phone: str | None = None
    profile_picture: str | None = None
    date_of_birth: date | None = None
    profession_id: UUID | None = None
    status: UserStatus | None = None
    roles: list[str] = pydantic.Field(
        default_factory=list, description="Role names to be assigned"
    )
    user_specialties: list[UserSpecialtyCreateForUserRequest] = pydantic.Field(
        default_factory=list,
        description="Lista de especialidades para vincular ao usuário no cadastro",
    )


class UserCreateRequestForm(UserCreateRequest):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    profile_picture_file: UploadFile | None = None

    @pydantic.field_validator(
        "cpf", "email", "phone", "password", "status", mode="before", check_fields=False
    )
    @classmethod
    def _normalize_fields(cls, v: Any, info: pydantic.ValidationInfo) -> Any:
        if v == "":
            return None
        if info.field_name == "status" and isinstance(v, str):
            v = v.upper()
        return v

    @classmethod
    def as_form(
        cls,
        first_name: str = Form(...),
        last_name: str = Form(...),
        cpf: str = Form(...),
        password: str | None = Form(None),
        email: str = Form(...),
        phone: str | None = Form(None),
        profile_picture_file: UploadFile | None = File(None),
        date_of_birth: date | None = Form(None),
        profession_id: UUID | None = Form(None),
        status: str | None = Form(None),
        roles: list[str] = Form(default_factory=list, alias="roles[]"),
    ) -> "UserCreateRequestForm":
        # Merge the lists in case frontend sends it via roles or roles[]
        return cls(
            first_name=first_name,
            last_name=last_name,
            cpf=cpf,
            password=password,
            email=email,
            phone=phone,
            profile_picture_file=profile_picture_file,
            date_of_birth=date_of_birth,
            profession_id=profession_id,
            status=status,
            roles=roles,
        )


class UserUpdateRequest(pydantic.BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    cpf: str | None = None
    password: str | None = None
    email: str | None = None
    phone: str | None = None
    profile_picture: str | None = None
    date_of_birth: date | None = None
    profession_id: UUID | None = None
    status: UserStatus | None = None
    roles: list[str] = pydantic.Field(
        default_factory=list, description="Role names to be assigned if updated"
    )


class UserUpdateRequestForm(UserUpdateRequest):
    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    profile_picture_file: UploadFile | None = None

    @pydantic.field_validator(
        "cpf", "email", "phone", "password", "status", mode="before", check_fields=False
    )
    @classmethod
    def _normalize_fields(cls, v: Any, info: pydantic.ValidationInfo) -> Any:
        if v == "":
            return None
        if info.field_name == "status" and isinstance(v, str):
            v = v.upper()
        return v

    @classmethod
    def as_form(
        cls,
        first_name: str | None = Form(None),
        last_name: str | None = Form(None),
        cpf: str | None = Form(None),
        password: str | None = Form(None),
        email: str | None = Form(None),
        phone: str | None = Form(None),
        profile_picture_file: UploadFile | None = File(None),
        date_of_birth: date | None = Form(None),
        profession_id: UUID | None = Form(None),
        status: str | None = Form(None),
        roles: list[str] = Form(default_factory=list, alias="roles[]"),
    ) -> "UserUpdateRequestForm":
        return cls(
            first_name=first_name,
            last_name=last_name,
            cpf=cpf,
            password=password,
            email=email,
            phone=phone,
            profile_picture_file=profile_picture_file,
            date_of_birth=date_of_birth,
            profession_id=profession_id,
            status=status,
            roles=roles,
        )


class ChangePasswordRequest(pydantic.BaseModel):
    old_password: str
    new_password: str


class UserListResponse(PaginatedResponse):
    """User list response with pagination."""

    data: list[UserResponse]
