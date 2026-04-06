"""User validator module."""

import re

from app.api.schemas.user import UserCreateRequest
from app.api.validators.user_specialty import UserSpecialtyValidator
from app.core.cpf import Cpf
from app.core.exceptions import BadRequestException


class UserValidator:
    def __init__(self) -> None:
        self.required_fields = ["first_name", "last_name", "cpf", "email"]

    def validate(self, user: UserCreateRequest) -> UserCreateRequest:

        for field in self.required_fields:
            if not getattr(user, field):
                raise BadRequestException(f"O campo '{field}' é obrigatório.")

        user.cpf = self.cpf_validator(user.cpf)

        if user.user_specialties:
            primary_count = sum(1 for item in user.user_specialties if item.is_primary)
            if primary_count > 1:
                raise BadRequestException("Only one primary specialty is allowed")

            for item in user.user_specialties:
                if not UserSpecialtyValidator.validate_specialty_id(item.specialty_id):
                    raise BadRequestException("Especialidade invalida")

        return user

    def cpf_validator(self, cpf: str) -> str:
        cpf = str(cpf).strip()
        cpf = "".join(filter(str.isdigit, cpf))

        if not Cpf.validate(cpf):
            raise BadRequestException("CPF invalido")

        return cpf

    def phone_validator(self, phone: str) -> str:
        phone = str(phone).strip()

        celular_pattern = r"^\(\d{2}\) \d{5}-\d{4}$"
        fixo_pattern = r"^\(\d{2}\) \d{4}-\d{4}$"

        if not (re.match(celular_pattern, phone) or re.match(fixo_pattern, phone)):
            raise BadRequestException(
                "Telefone invalido - deve ter o formato (99) 99999-9999 ou (99) 9999-9999"
            )

        return phone
