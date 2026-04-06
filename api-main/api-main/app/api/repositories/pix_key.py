"""Pix key repository."""

from uuid import UUID

import structlog
from fastapi import Depends
from sqlalchemy import select

from app.api.models.pix_key import PixKey
from app.api.schemas.pix_key import PixKeyCreateRequest, PixKeyResponse, PixKeyUpdateRequest
from app.core.exceptions import NotFoundException, ResourceAlreadyExistsException
from app.db.session import AsyncSession, get_db_session

logger = structlog.get_logger(__name__)


class PixKeyRepository:
    """Pix key repository."""

    def __init__(self, db: AsyncSession = Depends(get_db_session)):
        self.db = db

    async def get_pix_keys(self, include_inactive: bool = False) -> list[PixKeyResponse]:
        """Get all pix keys."""
        logger.debug("get_pix_keys called")
        query = select(PixKey)

        if not include_inactive:
            query = query.where(PixKey.is_active)

        result = await self.db.execute(query)
        pix_keys = result.scalars().all()
        logger.debug(f"Retrieved {len(pix_keys)} pix keys")

        return [PixKeyResponse.model_validate(pix_key) for pix_key in pix_keys]

    async def get_pix_key_by_id(self, pix_key_id: UUID) -> PixKeyResponse | None:
        """Get a pix key by id."""
        logger.debug(f"get_pix_key_by_id called for pix_key_id={pix_key_id}")
        result = await self.db.execute(select(PixKey).where(PixKey.id == pix_key_id))
        pix_key = result.scalar_one_or_none()
        logger.debug(f"Pix key found: {pix_key is not None}")

        if not pix_key:
            raise NotFoundException("Pix key not found")

        return PixKeyResponse.model_validate(pix_key)

    async def get_pix_keys_by_user_id(
        self, user_id: UUID, include_inactive: bool = False
    ) -> list[PixKeyResponse]:
        """Get pix keys by user id."""
        logger.debug(f"get_pix_keys_by_user_id called for user_id={user_id}")

        query = select(PixKey).where(PixKey.user_id == user_id)

        if not include_inactive:
            query = query.where(PixKey.is_active)

        result = await self.db.execute(query)
        pix_keys = result.scalars().all()
        logger.debug(f"Found {len(pix_keys)} pix keys")

        return [PixKeyResponse.model_validate(pix_key) for pix_key in pix_keys]

    async def get_main_pix_key_by_user_id(self, user_id: UUID) -> PixKeyResponse | None:
        """Get main pix key by user id."""
        logger.debug(f"get_main_pix_key_by_user_id called for user_id={user_id}")
        result = await self.db.execute(
            select(PixKey).where(PixKey.user_id == user_id, PixKey.is_main, PixKey.is_active)
        )
        pix_key = result.scalar_one_or_none()
        logger.debug(f"Main pix key found: {pix_key is not None}")

        if not pix_key:
            return None

        return PixKeyResponse.model_validate(pix_key)

    async def get_pix_key_by_code(self, code: str) -> PixKeyResponse | None:
        """Get pix key by code."""
        logger.debug(f"get_pix_key_by_code called for code={code}")
        result = await self.db.execute(select(PixKey).where(PixKey.code == code))
        pix_key = result.scalar_one_or_none()
        logger.debug(f"Pix key found: {pix_key is not None}")

        if not pix_key:
            return None

        return PixKeyResponse.model_validate(pix_key)

    async def create_pix_key(self, pix_key: PixKeyCreateRequest) -> PixKeyResponse:
        """Create a pix key."""
        logger.debug("create_pix_key called")

        # Check if code already exists
        existing = await self.get_pix_key_by_code(pix_key.code)
        if existing:
            raise ResourceAlreadyExistsException(resource_name="Chave Pix")

        # If this is set as main, unset all other main pix keys for this user
        if pix_key.is_main:
            await self._unset_main_pix_keys(pix_key.user_id)

        pix_key_data = pix_key.model_dump()
        new_pix_key = PixKey(**pix_key_data)

        self.db.add(new_pix_key)
        await self.db.commit()
        await self.db.refresh(new_pix_key)

        return PixKeyResponse.model_validate(new_pix_key)

    async def update_pix_key(
        self, pix_key_id: UUID, pix_key_data: PixKeyUpdateRequest
    ) -> PixKeyResponse:
        """Update a pix key."""
        logger.debug(f"update_pix_key called for pix_key_id={pix_key_id}")

        result = await self.db.execute(select(PixKey).where(PixKey.id == pix_key_id))
        pix_key = result.scalar_one_or_none()

        if not pix_key:
            raise NotFoundException("Pix key not found")

        # Check if updating code and if it conflicts with existing pix key
        if pix_key_data.code and pix_key_data.code != pix_key.code:
            existing = await self.get_pix_key_by_code(pix_key_data.code)
            if existing:
                raise ResourceAlreadyExistsException(resource_name="Chave Pix")

        # If this is set as main, unset all other main pix keys for this user
        if pix_key_data.is_main is True:
            await self._unset_main_pix_keys(pix_key.user_id, exclude_id=pix_key_id)

        for key, value in pix_key_data.model_dump(exclude_unset=True).items():
            setattr(pix_key, key, value)

        await self.db.commit()
        await self.db.refresh(pix_key)

        return PixKeyResponse.model_validate(pix_key)

    async def delete_pix_key(self, pix_key_id: UUID) -> None:
        """Delete a pix key."""
        logger.debug(f"delete_pix_key called for pix_key_id={pix_key_id}")
        result = await self.db.execute(select(PixKey).where(PixKey.id == pix_key_id))
        pix_key = result.scalar_one_or_none()

        if not pix_key:
            raise NotFoundException("Pix key not found")

        await self.db.delete(pix_key)
        await self.db.commit()

    async def _unset_main_pix_keys(self, user_id: UUID, exclude_id: UUID | None = None) -> None:
        """Unset all main pix keys for a user."""
        logger.debug(f"_unset_main_pix_keys called for user_id={user_id}")
        query = select(PixKey).where(PixKey.user_id == user_id, PixKey.is_main)

        if exclude_id:
            query = query.where(PixKey.id != exclude_id)

        result = await self.db.execute(query)
        pix_keys = result.scalars().all()

        for pix_key in pix_keys:
            pix_key.is_main = False

        await self.db.commit()
