import re
from typing import Any

from pydantic_core import core_schema
from sqlalchemy.types import String, TypeDecorator


class Cnpj:
    """
    Value Object representing a Brazilian CNPJ (Cadastro Nacional da Pessoa Jurídica).
    Handles validation, formatting, and raw value storage.
    """

    _value: str

    def __init__(self, value: "str | int | Cnpj"):
        if isinstance(value, Cnpj):
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
        """Returns the raw 14-digit string."""
        return self._value

    @property
    def formatted(self) -> str:
        """Returns the CNPJ formatted as XX.XXX.XXX/XXXX-XX."""
        return f"{self._value[:2]}.{self._value[2:5]}.{self._value[5:8]}/{self._value[8:12]}-{self._value[12:]}"

    def __str__(self) -> str:
        return self.formatted

    def __repr__(self) -> str:
        return f"Cnpj('{self.formatted}')"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Cnpj):
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
        Validates the CNPJ checksum and structure.
        Raises ValueError if invalid.
        """
        if len(value) != 14:
            raise ValueError("CNPJ must have 14 digits")

        if len(set(value)) == 1:
            raise ValueError("CNPJ cannot have all digits equal")

        weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_val = sum(int(value[i]) * weights1[i] for i in range(12))
        remainder = sum_val % 11
        if remainder < 2:
            digit1 = 0
        else:
            digit1 = 11 - remainder

        if digit1 != int(value[12]):
            raise ValueError("Invalid CNPJ digits")

        weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        sum_val = sum(int(value[i]) * weights2[i] for i in range(13))
        remainder = sum_val % 11
        if remainder < 2:
            digit2 = 0
        else:
            digit2 = 11 - remainder

        if digit2 != int(value[13]):
            raise ValueError("Invalid CNPJ digits")


class CnpjType(TypeDecorator):
    """
    SQLAlchemy TypeDecorator for Cnpj Value Object.

    - Stores as a VARCHAR(14) in the database (raw digits).
    - Returns a Cnpj object when read from database.
    - Accepts Cnpj object or string when setting values.
    """

    impl = String(14)

    cache_ok = True

    def process_bind_param(self, value: Cnpj | str | None, dialect: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, Cnpj):
            return value.value
        return Cnpj(value).value

    def process_result_value(self, value: str | None, dialect: Any) -> Cnpj | None:
        if value is None:
            return None
        return Cnpj(value)
