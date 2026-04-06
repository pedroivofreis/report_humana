import re

import structlog

from app.api.schemas.address import AddressCreateRequest, AddressUpdateRequest
from app.api.validators.base import BaseValidator
from app.core.exceptions import ValidationException

logger = structlog.get_logger(__name__)


class AddressValidator:
    """Business validation for addresses."""

    ZIP_CODE_REGEX = re.compile(r"^\d{5}-\d{3}$")
    ZIP_CODE_LENGTH = 9

    UF_REGEX = re.compile(r"^[A-Z]{2}$")
    UF_LENGTH = 2

    UF_LIST = [
        "AC",
        "AL",
        "AP",
        "AM",
        "BA",
        "CE",
        "DF",
        "ES",
        "GO",
        "MA",
        "MT",
        "MS",
        "MG",
        "PA",
        "PB",
        "PR",
        "PE",
        "PI",
        "RJ",
        "RN",
        "RS",
        "RO",
        "RR",
        "SC",
        "SP",
        "SE",
        "TO",
    ]

    @staticmethod
    def validate(address: AddressCreateRequest | AddressUpdateRequest) -> None:
        """
        Validate complete address data.

        Args:
            address: The address request data to validate

        Raises:
            ValidationException: If any validation fails
        """

        AddressValidator.validate_zip_code(address.zip_code)

        BaseValidator.validate_number(address.number)

        AddressValidator.validate_uf(address.uf)

    @staticmethod
    def validate_zip_code(zip_code: str | None) -> None:
        """
        Validate zip code format.

        Args:
            zip_code: The zip code to validate (format: 00000-000 or 00000000)

        Raises:
            ValidationException: If zip code format is invalid
        """
        if not zip_code:
            return

        # Remove hyphen to check digits
        cleaned_zip = zip_code.replace("-", "")

        if not cleaned_zip.isdigit() or len(cleaned_zip) != 8:
            raise ValidationException("Zip code must have 8 digits")

    @staticmethod
    def validate_uf(uf: str | None) -> None:
        """
        Validate UF format.

        Args:
            uf: The state to validate (format: SP, RJ, etc.)

        Raises:
            ValidationException: If UF format is invalid
        """

        if not uf:
            return

        uf = uf.upper()

        if len(uf) != AddressValidator.UF_LENGTH or not AddressValidator.UF_REGEX.match(uf):
            raise ValidationException("UF must be a 2-letter code (e.g., SP, RJ)")

        if uf not in AddressValidator.UF_LIST:
            raise ValidationException(
                f"UF must be a valid state code: {', '.join(AddressValidator.UF_LIST)}"
            )
