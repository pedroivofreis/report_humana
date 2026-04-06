from uuid import UUID

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    id: UUID


class LoginRequest(BaseModel):
    cpf: str
    password: str
    remember_me: bool = False


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    cpf: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
