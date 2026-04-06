"""User model module."""

from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.core.cpf import Cpf, CpfType
from app.core.phone import Phone, PhoneType
from app.db.session import Base

if TYPE_CHECKING:
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


class UserStatus(str, enum.Enum):
    """User status enum."""

    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    WITH_PENDENCY = "WITH_PENDENCY"
    RESCISSION = "RESCISSION"
    ENROLLED = "ENROLLED"


class User(Base):
    """User model."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid7, index=True)
    profession_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("professions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        Enum(
            "REGISTERED",
            "ACTIVE",
            "INACTIVE",
            "WITH_PENDENCY",
            "RESCISSION",
            "ENROLLED",
            name="user_status",
            native_enum=False,
        ),
        nullable=False,
        default=UserStatus.REGISTERED,
        server_default=UserStatus.REGISTERED.value,
    )
    pendency: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )
    cpf: Mapped[Cpf] = mapped_column(CpfType, nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[Phone | None] = mapped_column(PhoneType, nullable=True)
    profile_picture: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    # Relationships
    profession: Mapped[Profession | None] = relationship("Profession", back_populates="users")
    complementary_data: Mapped[ComplementaryData | None] = relationship(
        "ComplementaryData", back_populates="user", uselist=False
    )
    user_roles: Mapped[list[UserRole]] = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    address: Mapped[Address | None] = relationship("Address", back_populates="user", uselist=False)
    bank_accounts: Mapped[list[BankAccount]] = relationship(
        "BankAccount", back_populates="user", cascade="all, delete-orphan"
    )
    user_specialties: Mapped[list[UserSpecialty]] = relationship(
        "UserSpecialty", back_populates="user", cascade="all, delete-orphan"
    )
    pix_keys: Mapped[list[PixKey]] = relationship(
        "PixKey", back_populates="user", cascade="all, delete-orphan"
    )
    absences: Mapped[list[UserAbsence]] = relationship(
        "UserAbsence", back_populates="user", cascade="all, delete-orphan"
    )
    professional_crms: Mapped[list[ProfessionalCrm]] = relationship(
        "ProfessionalCrm", back_populates="user", cascade="all, delete-orphan"
    )
    institution_contracts: Mapped[list[InstitutionContract]] = relationship(
        "InstitutionContract", back_populates="user", cascade="all, delete-orphan"
    )
    received_observations: Mapped[list["UserObservation"]] = relationship(
        "UserObservation",
        foreign_keys="[UserObservation.target_user_id]",
        back_populates="target_user",
        cascade="all, delete-orphan",
    )
    made_observations: Mapped[list["UserObservation"]] = relationship(
        "UserObservation",
        foreign_keys="[UserObservation.owner_id]",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
    location_bindings: Mapped[list["ProfessionalLocationBinding"]] = relationship(
        "ProfessionalLocationBinding", back_populates="user", cascade="all, delete-orphan"
    )
