"""Bank account model module."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid_utils import uuid7

from app.db.session import Base

if TYPE_CHECKING:
    from app.api.models.user import User


class BankAccount(Base):
    """Bank account model."""

    __tablename__ = "bank_accounts"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, index=True, default=uuid7)
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    bank_code: Mapped[str] = mapped_column(String(10), nullable=False)
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    agency: Mapped[str] = mapped_column(String(10), nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), nullable=False)
    account_digit: Mapped[str] = mapped_column(String(2), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=text("CURRENT_TIMESTAMP"), nullable=True
    )

    user: Mapped[User | None] = relationship("User", back_populates="bank_accounts")

    def __repr__(self) -> str:
        return f"<BankAccount(id={self.id}, bank_name={self.bank_name}, account_number={self.account_number}, is_main={self.is_main})>"
