from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    """
    Returns the hash of the password using the recommended algorithm (likely Argon2).
    """
    return str(password_hash.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against the hashed password.
    """
    return bool(password_hash.verify(plain_password, hashed_password))


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Creates a JWT access token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), **(extra_claims or {})}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(encoded_jwt)


def create_refresh_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """
    Creates a JWT refresh token.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {"exp": expire, "sub": str(subject), "refresh": True}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(encoded_jwt)


def create_password_reset_token(subject: str | Any) -> str:
    """
    Creates a JWT password reset token.
    """
    expire = datetime.now(UTC) + timedelta(hours=1)
    to_encode = {"exp": expire, "sub": str(subject), "reset": True}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(encoded_jwt)
