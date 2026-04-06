from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError

from app.api.repositories.user import UserRepository
from app.api.schemas.auth import TokenData
from app.api.schemas.user import UserResponse
from app.core.config import settings

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_STR}/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
) -> UserResponse | None:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: UUID = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except (jwt.PyJWTError, ValidationError):
        raise credentials_exception from None

    user = await user_repository.get_user_by_id(user_id=token_data.id)
    if user is None:
        raise credentials_exception
    return user


class RoleChecker:
    def __init__(self, allowed_roles: list[str]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self, user: Annotated[UserResponse, Depends(get_current_user)]
    ) -> UserResponse | None:
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")

        user_roles = [role.name for role in user.roles]
        if any(role in user_roles for role in self.allowed_roles):
            return user

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation not permitted")

import fastapi
async def get_optional_current_user(
    request: fastapi.Request,
    user_repository: Annotated[UserRepository, Depends(UserRepository)],
) -> UserResponse | None:
    """Gets the current user if a token is provided in the Authorization header, else None."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
        
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        token_data = TokenData(id=UUID(user_id_str))
    except (jwt.PyJWTError, ValidationError, ValueError):
        return None

    # Fetch user
    return await user_repository.get_user_by_id(user_id=token_data.id)

class CreateUserRoleChecker:
    """
    Dependency that conditionally checks the current user's roles.
    If the incoming request wants to create a 'manager' or 'admin',
    the request MUST be authenticated and the user MUST be an 'admin'.
    """
    
    async def __call__(
        self,
        request: fastapi.Request,
        user_repository: Annotated[UserRepository, Depends(UserRepository)]
    ) -> None:
        
        # We need to parse the incoming form or JSON to see what roles they asked for.
        # Wait for the body parsing:
        form_data = await request.form()
        roles_requested = form_data.getlist("roles")
        
        if not roles_requested:
            roles_requested = form_data.getlist("roles[]")
        
        if not roles_requested:
            # Maybe it's a JSON body instead?
            try:
                json_data = await request.json()
                roles_requested = json_data.get("roles", [])
            except Exception:
                pass

        if "admin" in roles_requested or "manager" in roles_requested:
            current_user = await get_optional_current_user(request, user_repository)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Autenticação necessária para criar cargos de administrador ou gerente"
                )
            
            user_roles = [r.name for r in current_user.roles]
            if "admin" not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Apenas administradores podem criar usuários com cargos de administrador ou gerente"
                )

class UpdateUserRoleChecker(CreateUserRoleChecker):
    """
    Dependency to conditionally check if user can update roles.
    Follows same structure as Create checker, but throws specific errors for edits if needed.
    """
    async def __call__(
        self,
        request: fastapi.Request,
        user_repository: Annotated[UserRepository, Depends(UserRepository)]
    ) -> None:
        form_data = await request.form()
        roles_requested = form_data.getlist("roles")
        if not roles_requested:
            roles_requested = form_data.getlist("roles[]")
            
        if not roles_requested:
            try:
                json_data = await request.json()
                roles_requested = json_data.get("roles", [])
            except Exception:
                pass

        if "admin" in roles_requested or "manager" in roles_requested:
            current_user = await get_optional_current_user(request, user_repository)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, 
                    detail="Autenticação necessária para promover um usuário a administrador ou gerente"
                )
            
            user_roles = [r.name for r in current_user.roles]
            if "admin" not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, 
                    detail="Apenas administradores podem promover outros usuários a administrador ou gerente"
                )
