"""User repository."""

import math
import uuid
from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.api.models.user import User, UserStatus
from app.api.models.role import Role
from app.api.models.user_role import UserRole
from app.api.models.user_specialty import UserSpecialty
from app.api.schemas.address import AddressResponse
from app.api.schemas.complementary_data import ComplementaryDataResponse
from app.api.schemas.profession import ProfessionResponse
from app.api.schemas.role import RoleResponse
from app.api.schemas.user import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserResponseById,
    UserUpdateRequest,
)
from app.api.schemas.user_specialty import UserSpecialtyWithDetailsResponse
from app.core.cpf import Cpf
from app.core.security import get_password_hash
from app.db.session import AsyncSession, get_db_session

logger = structlog.getLogger(__name__)


class UserRepository:
    """User repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_users(
        self,
        page: int = 1,
        page_size: int = 10,
        is_active: bool | None = None,
        name: str | None = None,
        status: UserStatus | None = None,
        role: list[str] | None = None,
    ) -> UserListResponse:
        """Get all users with pagination and filters."""
        logger.debug(
            f"get_users called with page={page}, page_size={page_size}, is_active={is_active}, "
            f"name={name}, status={status}, role={role}"
        )

        filters = []
        if is_active is not None:
            filters.append(User.is_active == is_active)

        if status:
            filters.append(User.status == status)

        if name:
            name = name.strip()
            if name:
                search_pattern = f"%{name}%"
                filters.append(
                    or_(
                        User.first_name.ilike(search_pattern),
                        User.last_name.ilike(search_pattern),
                        (User.first_name + " " + User.last_name).ilike(search_pattern),
                    )
                )

        if role:
            filters.append(User.user_roles.any(UserRole.role.has(Role.name.in_(role))))

        query = (
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .options(selectinload(User.profession))
            .options(selectinload(User.user_specialties).selectinload(UserSpecialty.specialty))
            .order_by(User.created_at.desc(), User.id)
        )

        if filters:
            query = query.where(*filters)

        count_query = select(func.count(User.id)).select_from(User)
        if filters:
            count_query = count_query.where(*filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        result = await self.db.execute(query)
        users = result.scalars().all()
        logger.debug(f"Retrieved {len(users)} users out of {total} total")

        users_response = []
        for user in users:
            base = UserResponse.model_validate(user)
            users_response.append(
                base.model_copy(
                    update={
                        "roles": [RoleResponse.model_validate(ur.role) for ur in user.user_roles],
                        "profession": (
                            ProfessionResponse.model_validate(user.profession)
                            if user.profession
                            else None
                        ),
                        "user_specialties": [
                            UserSpecialtyWithDetailsResponse.model_validate(up)
                            for up in user.user_specialties
                        ],
                    }
                )
            )

        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return UserListResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            data=users_response,
        )

    async def get_user_by_id(self, user_id: UUID) -> UserResponseById | None:
        """Get a user by id."""
        logger.debug(f"get_user_by_id called for user_id={user_id}")
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .options(selectinload(User.complementary_data))
            .options(selectinload(User.address))
            .options(selectinload(User.bank_accounts))
            .options(selectinload(User.profession))
            .options(selectinload(User.user_specialties).selectinload(UserSpecialty.specialty))
            .options(selectinload(User.pix_keys))
        )
        user = result.scalar_one_or_none()
        logger.debug(f"User found: {user is not None}")

        if not user:
            return None

        user_dict = UserResponseById.model_validate(user).model_dump()
        user_dict["roles"] = [RoleResponse.model_validate(ur.role) for ur in user.user_roles]
        if user.profession:
            user_dict["profession"] = ProfessionResponse.model_validate(user.profession)
        if user.complementary_data:
            user_dict["complementary_data"] = ComplementaryDataResponse.model_validate(
                user.complementary_data
            )
        if user.address:
            user_dict["address"] = AddressResponse.model_validate(user.address)
        return UserResponseById(**user_dict)

    async def get_user_by_email(self, email: str) -> UserResponse | None:
        """Get a user by email."""
        logger.debug(f"get_user_by_email called for email={email}")
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .options(selectinload(User.profession))
        )
        user = result.scalar_one_or_none()
        logger.debug(f"User found: {user is not None}")

        if not user:
            return None

        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            status=user.status,
            cpf=user.cpf,
            email=user.email,
            phone=user.phone,
            profile_picture=user.profile_picture,
            date_of_birth=user.date_of_birth,
            profession=(
                ProfessionResponse.model_validate(user.profession) if user.profession else None
            ),
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[RoleResponse.model_validate(ur.role) for ur in user.user_roles],
            user_specialties=[],
        )

    async def get_user_auth_data_by_email(self, email: str) -> User | None:
        """Get a user by email with password for authentication."""
        logger.debug(f"get_user_auth_data_by_email called for email={email}")
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return result.scalar_one_or_none()

    async def get_user_auth_data_by_cpf(self, cpf: str) -> User | None:
        """Get a user by CPF with password for authentication."""
        if not Cpf.validate(cpf):
            logger.info("get_user_auth_data_by_cpf received invalid cpf format")
            return None
        result = await self.db.execute(
            select(User)
            .where(User.cpf == cpf)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return result.scalar_one_or_none()

    async def get_user_by_cpf(self, cpf: str) -> UserResponse | None:
        """Get a user by CPF."""
        logger.debug(f"get_user_by_cpf called for cpf={cpf}")
        if not Cpf.validate(cpf):
            logger.info("get_user_by_cpf received invalid cpf format")
            return None
        result = await self.db.execute(
            select(User)
            .where(User.cpf == cpf)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .options(selectinload(User.profession))
        )
        user = result.scalar_one_or_none()
        logger.debug(f"User found: {user is not None}")

        if not user:
            return None

        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            status=user.status,
            cpf=user.cpf,
            email=user.email,
            phone=user.phone,
            profile_picture=user.profile_picture,
            date_of_birth=user.date_of_birth,
            profession=(
                ProfessionResponse.model_validate(user.profession) if user.profession else None
            ),
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[RoleResponse.model_validate(ur.role) for ur in user.user_roles],
            user_specialties=[],
        )

    async def get_user_by_phone(self, phone: str | None = None) -> UserResponse | None:
        """Get a user by phone."""
        logger.debug(f"get_user_by_phone called for phone={phone}")
        if not phone:
            return None
        result = await self.db.execute(
            select(User)
            .where(User.phone == phone)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .options(selectinload(User.profession))
        )
        user = result.scalar_one_or_none()
        logger.debug(f"User found: {user is not None}")

        if not user:
            return None

        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            status=user.status,
            cpf=user.cpf,
            email=user.email,
            phone=user.phone,
            profile_picture=user.profile_picture,
            date_of_birth=user.date_of_birth,
            profession=(
                ProfessionResponse.model_validate(user.profession) if user.profession else None
            ),
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=[RoleResponse.model_validate(ur.role) for ur in user.user_roles],
            user_specialties=[],
        )

    async def create_user(self, user: UserCreateRequest) -> UserResponse:
        """Create a user."""
        logger.debug("create_user called")

        user_data = user.model_dump(
            exclude={"roles", "user_specialties", "profile_picture_file"}
        )
        new_user = User(**user_data)
        if not user.password:
            user.password = str(uuid.uuid4())

        new_user.password = get_password_hash(user.password)

        self.db.add(new_user)
        await self.db.flush()

        role_ids = []
        if user.roles:
            result_roles = await self.db.execute(select(Role).where(Role.name.in_(user.roles)))
            for role in result_roles.scalars().all():
                role_ids.append(role.id)
            
            # If no roles were given or valid, default to 'professional'
            if not role_ids:
                default_role = await self.db.execute(select(Role).where(Role.name == "professional"))
                prof_role = default_role.scalar_one_or_none()
                if prof_role:
                    role_ids.append(prof_role.id)
        else:
            default_role = await self.db.execute(select(Role).where(Role.name == "professional"))
            prof_role = default_role.scalar_one_or_none()
            if prof_role:
                role_ids.append(prof_role.id)

        for role_id in role_ids:
            user_role = UserRole(user_id=new_user.id, role_id=role_id)
            self.db.add(user_role)

        if user.user_specialties:
            for item in user.user_specialties:
                self.db.add(
                    UserSpecialty(
                        user_id=new_user.id,
                        specialty_id=item.specialty_id,
                        is_primary=item.is_primary,
                    )
                )

        await self.db.commit()
        await self.db.refresh(new_user, ["user_roles"])

        result = await self.db.execute(
            select(User)
            .where(User.id == new_user.id)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .options(selectinload(User.profession))
            .options(selectinload(User.user_specialties).selectinload(UserSpecialty.specialty))
        )
        new_user = result.scalar_one()

        base = UserResponse.model_validate(new_user)
        return base.model_copy(
            update={
                "roles": [RoleResponse.model_validate(ur.role) for ur in new_user.user_roles],
                "profession": (
                    ProfessionResponse.model_validate(new_user.profession)
                    if new_user.profession
                    else None
                ),
                "user_specialties": [
                    UserSpecialtyWithDetailsResponse.model_validate(up)
                    for up in new_user.user_specialties
                ],
            }
        )

    async def update_user(self, user_id: UUID, userData: UserUpdateRequest) -> UserResponse:
        """Update a user."""
        logger.debug(f"update_user called for user_id={user_id}")

        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        user = result.scalar_one()

        for key, value in userData.model_dump(
            exclude_unset=True, exclude={"profile_picture_file", "roles"}
        ).items():
            if key == "password":
                if value:
                    user.password = get_password_hash(value)
            elif value is not None:
                setattr(user, key, value)

        await self.db.commit()
        
        # Role update logic
        if userData.roles is not None and len(userData.roles) > 0:
            # Use SQLAlchemy ORM relation mapping properly instead of raw SQL
            # to make sure the session's identity map correctly synchronizes
            user.user_roles = []
            
            result_roles = await self.db.execute(select(Role).where(Role.name.in_(userData.roles)))
            for role in result_roles.scalars().all():
                new_ur = UserRole(user_id=user_id, role_id=role.id)
                user.user_roles.append(new_ur)
                self.db.add(new_ur)
                
        await self.db.commit()
        result = await self.db.execute(
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .options(selectinload(User.profession))
            .options(selectinload(User.user_specialties).selectinload(UserSpecialty.specialty))
        )
        user = result.scalar_one()

        base = UserResponse.model_validate(user)
        return base.model_copy(
            update={
                "roles": [RoleResponse.model_validate(ur.role) for ur in user.user_roles],
                "profession": (
                    ProfessionResponse.model_validate(user.profession) if user.profession else None
                ),
                "user_specialties": [
                    UserSpecialtyWithDetailsResponse.model_validate(up)
                    for up in user.user_specialties
                ],
            }
        )

    async def delete_user(self, user_id: UUID) -> None:
        """Delete a user."""
        logger.debug(f"delete_user called for user_id={user_id}")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            return None

        await self.db.delete(user)
        await self.db.commit()

    async def update_password(self, user_id: UUID, hashed_password: str) -> None:
        """Update user password."""
        logger.debug(f"update_password called for user_id={user_id}")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        user.password = hashed_password
        await self.db.commit()
