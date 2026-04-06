from datetime import timedelta
from uuid import UUID

import structlog
from fastapi import Depends

from app.api.repositories.user import UserRepository
from app.api.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    Token,
)
from app.core.config import settings
from app.core.email import EmailService
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)

logger = structlog.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository = Depends(UserRepository),
        email_service: EmailService = Depends(EmailService),
    ):
        self.user_repository = user_repository
        self.email_service = email_service

    async def authenticate_user(self, login_request: LoginRequest) -> Token:
        user = await self.user_repository.get_user_auth_data_by_cpf(login_request.cpf)
        if not user or not user.password:
            raise BadRequestException("Incorrect CPF or password")

        if not verify_password(login_request.password, user.password):
            raise BadRequestException("Incorrect CPF or password")

        if not user.is_active:
            raise BadRequestException("User is inactive")

        if login_request.remember_me:
            access_token_expires = timedelta(days=7)
        else:
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        extra_claims = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "roles": [ur.role.name for ur in user.user_roles],
        }
        access_token = create_access_token(
            subject=user.id, expires_delta=access_token_expires, extra_claims=extra_claims
        )
        refresh_token = create_refresh_token(
            subject=user.id, expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )

        return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)

    async def refresh_token(self, refresh_request: RefreshTokenRequest) -> Token:
        import jwt

        try:
            payload = jwt.decode(
                refresh_request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: UUID = payload.get("sub")
            if user_id is None:
                raise UnauthorizedException("Invalid refresh token")
        except jwt.PyJWTError:
            raise UnauthorizedException("Invalid refresh token") from None

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(subject=user_id, expires_delta=access_token_expires)

        return Token(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_request.refresh_token,
        )

    async def request_password_reset(self, request: ForgotPasswordRequest) -> None:
        user = await self.user_repository.get_user_auth_data_by_cpf(request.cpf)
        if not user or not user.is_active:
            return

        token = create_password_reset_token(user.id)
        print(token)
        await self.email_service.send_password_reset_email(user.email, token)

    async def reset_password(self, request: ResetPasswordRequest) -> None:
        import jwt

        try:
            payload = jwt.decode(
                request.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            user_id: UUID = payload.get("sub")
            is_reset: bool = payload.get("reset")
            if user_id is None or not is_reset:
                raise UnauthorizedException("Invalid reset token")
        except jwt.PyJWTError:
            raise UnauthorizedException("Invalid reset token") from None

        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UnauthorizedException("User not found")

        hashed_password = get_password_hash(request.new_password)
        await self.user_repository.update_password(user.id, hashed_password)
