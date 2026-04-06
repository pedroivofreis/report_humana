from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.api.dependencies.authentication import get_current_user
from app.api.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    ResetPasswordRequest,
    Token,
)
from app.api.schemas.user import UserResponseById
from app.api.services.auth import AuthService

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.get("/me", response_model=UserResponseById)
async def read_users_me(
    current_user: UserResponseById = Depends(get_current_user),
) -> UserResponseById:
    return current_user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
    request: Request, login_request: LoginRequest, auth_service: AuthService = Depends(AuthService)
) -> Token:
    return await auth_service.authenticate_user(login_request)


@router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest, auth_service: AuthService = Depends(AuthService)
) -> Token:
    return await auth_service.refresh_token(refresh_request)


@router.post("/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    forgot_request: ForgotPasswordRequest,
    auth_service: AuthService = Depends(AuthService),
) -> None:
    await auth_service.request_password_reset(forgot_request)


@router.post("/reset-password")
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    reset_request: ResetPasswordRequest,
    auth_service: AuthService = Depends(AuthService),
) -> None:
    await auth_service.reset_password(reset_request)
