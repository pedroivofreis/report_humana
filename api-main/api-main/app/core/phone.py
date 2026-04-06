import re
from typing import Any

from pydantic_core import core_schema
from sqlalchemy.types import String, TypeDecorator


class Phone:
    """
    Value Object representing a Brazilian Phone Number.
    Handles validation, formatting, and raw value storage.
    Supports 10 digits (Landline: XX XXXX-XXXX) and 11 digits (Mobile: XX XXXXX-XXXX).
    """

    _value: str

    def __init__(self, value: "str | int | Phone"):
        if isinstance(value, Phone):
            self._value = value._value
            return

        clean_value = self._clean(str(value))
        self._validate(clean_value)
        self._value = clean_value

    @property
    def value(self) -> str:
        """Returns the raw digit string."""
        return self._value

    @property
    def formatted(self) -> str:
        """Returns the Phone formatted."""
        if len(self._value) == 11:
            return f"({self._value[:2]}) {self._value[2:7]}-{self._value[7:]}"
        else:
            return f"({self._value[:2]}) {self._value[2:6]}-{self._value[6:]}"

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"Phone('{self.formatted}')"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Phone):
            return self._value == other._value
        if isinstance(other, str):
            try:
                return self._value == self._clean(other)
            except ValueError:
                return False
        return False

    @staticmethod
    def _clean(value: str) -> str:
        """Removes non-digit characters."""
        return re.sub(r"\D", "", value)

    @classmethod
    def validate(cls, value: str) -> bool:
        """Public validation method that returns boolean instead of raising."""
        try:
            clean_value = cls._clean(value)
            cls._validate(clean_value)
            return True
        except ValueError:
            return False

    @staticmethod
    def _validate(value: str) -> None:
        """
        Validates the Phone structure.
        Raises ValueError if invalid.
        """
        if len(value) not in (10, 11):
            raise ValueError("Telefone deve ter 10 ou 11 dígitos")

    @classmethod
    def _from_value(cls, value: Any) -> "Phone | None":
        """Tolerant factory used by Pydantic — returns None for invalid values instead of raising."""
        if isinstance(value, cls):
            return value
        if not value:
            return None
        try:
            return cls(value)
        except ValueError:
            return None

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        """
        Defines the Pydantic Core Schema for this type.
        Validates input as string/int and serializes to string.
        Invalid values (dirty DB data) are coerced to None.
        """
        return core_schema.no_info_plain_validator_function(
            cls._from_value,
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.formatted if instance else None,
                when_used="json",
            ),
        )


class PhoneType(TypeDecorator):
    """
    SQLAlchemy TypeDecorator for Phone Value Object.

    - Stores as a VARCHAR(11) in the database (raw digits).
    - Returns a Phone object when read from database.
    - Accepts Phone object or string when setting values.
    """

    impl = String(15)

    cache_ok = True

    def process_bind_param(self, value: Phone | str | None, dialect: Any) -> str | None:
        if not value:
            return None
        if isinstance(value, Phone):
            return value.formatted
        try:
            return Phone(value).formatted
        except ValueError:
            return None

    def process_result_value(self, value: str | None, dialect: Any) -> Phone | None:
        if value is None:
            return None
        try:
            return Phone(value)
        except ValueError:
            return None
