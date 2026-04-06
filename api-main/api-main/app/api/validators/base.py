"""Base validator module."""

from app.core.exceptions import ValidationException


class BaseValidator:
    """Base validator for all validators."""

    @staticmethod
    def validate_number(number: str | None) -> None:
        """
        Validate number format.

        Args:
            number: The number to validate
        """
        if number and not number.isdigit():
            raise ValidationException("Number must be a number")
