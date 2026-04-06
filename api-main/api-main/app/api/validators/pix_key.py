"""Pix key validator module."""

import re

import structlog

logger = structlog.get_logger(__name__)


class PixKeyValidator:
    """Pix key validator."""

    @staticmethod
    def validate_cpf(cpf: str) -> bool:
        """
        Validate CPF format.

        Args:
            cpf: CPF to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not cpf or not cpf.strip():
            return False

        # Remove non-numeric characters
        cpf_clean = re.sub(r"\D", "", cpf)

        # CPF must have 11 digits
        return len(cpf_clean) == 11 and cpf_clean.isdigit()

    @staticmethod
    def validate_cnpj(cnpj: str) -> bool:
        """
        Validate CNPJ format.

        Args:
            cnpj: CNPJ to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not cnpj or not cnpj.strip():
            return False

        # Remove non-numeric characters
        cnpj_clean = re.sub(r"\D", "", cnpj)

        # CNPJ must have 14 digits
        return len(cnpj_clean) == 14 and cnpj_clean.isdigit()

    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not email or not email.strip():
            return False

        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(email_pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone format.

        Args:
            phone: Phone to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not phone or not phone.strip():
            return False

        # Remove non-numeric characters
        phone_clean = re.sub(r"\D", "", phone)

        # Brazilian phone must have 10 or 11 digits (with area code)
        return len(phone_clean) in [10, 11] and phone_clean.isdigit()

    @staticmethod
    def validate_random_key(key: str) -> bool:
        """
        Validate random key format (UUID).

        Args:
            key: Random key to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not key or not key.strip():
            return False

        # Random key should be a UUID format (36 characters with hyphens)
        uuid_pattern = r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$"
        return bool(re.match(uuid_pattern, key.lower()))

    @staticmethod
    def validate_pix_key(key_type: str, key_value: str) -> bool:
        """
        Validate pix key based on type.

        Args:
            key_type: Type of the key (CPF, email, phone, random)
            key_value: Value of the key

        Returns:
            bool: True if valid, False otherwise
        """
        validators = {
            "CPF": PixKeyValidator.validate_cpf,
            "CNPJ": PixKeyValidator.validate_cnpj,
            "email": PixKeyValidator.validate_email,
            "phone": PixKeyValidator.validate_phone,
            "random": PixKeyValidator.validate_random_key,
        }

        validator = validators.get(key_type)
        if not validator:
            return False

        return validator(key_value)
