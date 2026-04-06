"""Bank account validator module."""

import structlog

logger = structlog.get_logger(__name__)


class BankAccountValidator:
    """Bank account validator."""

    @staticmethod
    def validate_bank_code(bank_code: str) -> bool:
        """
        Validate bank code format.

        Args:
            bank_code: Bank code to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not bank_code or not bank_code.strip():
            return False

        return bank_code.isdigit() and len(bank_code) >= 1 and len(bank_code) <= 10

    @staticmethod
    def validate_agency(agency: str) -> bool:
        """
        Validate agency format.

        Args:
            agency: Agency to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not agency or not agency.strip():
            return False

        return agency.replace("-", "").isdigit()

    @staticmethod
    def validate_account_number(account_number: str) -> bool:
        """
        Validate account number format.

        Args:
            account_number: Account number to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if not account_number or not account_number.strip():
            return False

        return account_number.replace("-", "").isdigit()

    @staticmethod
    def validate_account_type(account_type: str) -> bool:
        """
        Validate account type.

        Args:
            account_type: Account type to validate

        Returns:
            bool: True if valid, False otherwise
        """
        valid_types = ["checking", "savings", "payment", "salary"]
        return account_type.lower() in valid_types
