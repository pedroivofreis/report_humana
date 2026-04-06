import re
from typing import Any

from pydantic_core import core_schema
from sqlalchemy.types import String, TypeDecorator


class Cpf:
    """
    Value Object representing a Brazilian CPF (Cadastro de Pessoas Físicas).
    Handles validation, formatting, and raw value storage.
    """

    _value: str

    def __init__(self, value: "str | int | Cpf"):
        if isinstance(value, Cpf):
            self._value = value._value
            return

        clean_value = self._clean(str(value))
        self._validate(clean_value)
        self._value = clean_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: Any
    ) -> core_schema.CoreSchema:
        """
        Defines the Pydantic Core Schema for this type.
        Validates input as string/int and serializes to string.
        """
        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.union_schema(
                [
                    core_schema.str_schema(),
                    core_schema.int_schema(),
                    core_schema.is_instance_schema(cls),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.formatted,
                when_used="json",
            ),
        )

    @property
    def value(self) -> str:
        """Returns the raw 11-digit string."""
        return self._value

    @property
    def formatted(self) -> str:
        """Returns the CPF formatted as XXX.XXX.XXX-XX."""
        return f"{self._value[:3]}.{self._value[3:6]}.{self._value[6:9]}-{self._value[9:]}"

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"Cpf('{self.formatted}')"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Cpf):
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
        Validates the CPF checksum and structure.
        Raises ValueError if invalid.
        """
        if len(value) != 11:
            raise ValueError("CPF must have 11 digits")

        if len(set(value)) == 1:
            raise ValueError("CPF cannot have all digits equal")

        # First digit validation
        sum_val = sum(int(value[i]) * (10 - i) for i in range(9))
        digit1 = (sum_val * 10) % 11
        if digit1 == 10:
            digit1 = 0

        if digit1 != int(value[9]):
            raise ValueError("Invalid CPF digits")

        # Second digit validation
        sum_val = sum(int(value[i]) * (11 - i) for i in range(10))
        digit2 = (sum_val * 10) % 11
        if digit2 == 10:
            digit2 = 0

        if digit2 != int(value[10]):
            raise ValueError("Invalid CPF digits")


class CpfType(TypeDecorator):
    """
    SQLAlchemy TypeDecorator for Cpf Value Object.

    - Stores as a VARCHAR(11) in the database (raw digits).
    - Returns a Cpf object when read from database.
    - Accepts Cpf object or string when setting values.
    """

    impl = String(11)

    cache_ok = True

    def process_bind_param(self, value: Cpf | str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, Cpf):
            return value.value
        return Cpf(value).value

    def process_result_value(self, value: str | None, dialect: Any) -> Cpf | None:
        if value is None:
            return None
        return Cpf(value)
