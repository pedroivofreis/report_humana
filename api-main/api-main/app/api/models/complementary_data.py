"""Complementary data model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from uuid_utils import uuid7

from app.api.schemas.complementary_data import GenderEnum, MaritalStatusEnum, RaceEnum
from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.user import User


class ComplementaryData(Base):
    """Complementary data model."""

    __tablename__ = "complementary_data"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    marital_status: Mapped[MaritalStatusEnum | None] = mapped_column(
        Enum(MaritalStatusEnum), nullable=True
    )
    place_of_birth: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nationality: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mother_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    father_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    has_disability: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    disability: Mapped[str | None] = mapped_column(String(500), nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(Enum(GenderEnum), nullable=True)
    race: Mapped[RaceEnum | None] = mapped_column(Enum(RaceEnum), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    user: Mapped[User] = relationship("User", back_populates="complementary_data", uselist=False)
