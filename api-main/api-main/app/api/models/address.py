"""Address model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.institutions import Institution
    from app.api.models.user import User


class Address(Base):
    """Address model."""

    __tablename__ = "addresses"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=True, index=True
    )
    zip_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    street: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    number: Mapped[str] = mapped_column(String(25), nullable=False, index=True)
    complement: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    neighborhood: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    uf: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    user: Mapped[User | None] = relationship("User", back_populates="address")
    institution: Mapped[Institution | None] = relationship("Institution", back_populates="address")

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, zip_code={self.zip_code}, street={self.street}, number={self.number}, complement={self.complement}, neighborhood={self.neighborhood}, city={self.city}, uf={self.uf})>"
