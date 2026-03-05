"""API Key CRUD service."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_api_key, hash_key, verify_key, extract_prefix
from app.models.api_key import APIKey
from app.schemas.keys import KeyRead, KeyCreated
from app.utils.exceptions import KeyNotFoundError


class APIKeyService:
    """Handles API key creation, listing, and revocation."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, name: str) -> KeyCreated:
        """Create a new API key.

        Args:
            name: User-provided label for the key.

        Returns:
            KeyCreated schema with the full key (shown once).
        """
        raw_key = generate_api_key()
        key_record = APIKey(
            name=name,
            key_hash=hash_key(raw_key),
            key_prefix=extract_prefix(raw_key),
        )
        self.db.add(key_record)
        await self.db.commit()
        await self.db.refresh(key_record)

        return KeyCreated(
            id=key_record.id,
            name=key_record.name,
            key=raw_key,
            key_prefix=key_record.key_prefix,
            created_at=key_record.created_at,
        )

    async def list_all(self) -> list[KeyRead]:
        """List all active API keys (prefix + metadata only).

        Returns:
            List of KeyRead schemas.
        """
        result = await self.db.execute(
            select(APIKey).where(APIKey.is_active == True).order_by(APIKey.created_at.desc())
        )
        keys = result.scalars().all()

        return [
            KeyRead(
                id=k.id,
                name=k.name,
                key_prefix=k.key_prefix,
                created_at=k.created_at,
                last_used_at=k.last_used_at,
                is_active=k.is_active,
            )
            for k in keys
        ]

    async def revoke(self, key_id: str) -> dict:
        """Soft-delete an API key.

        Args:
            key_id: UUID of the key to revoke.

        Returns:
            Confirmation dict.

        Raises:
            KeyNotFoundError: If the key doesn't exist.
        """
        result = await self.db.execute(
            select(APIKey).where(APIKey.id == uuid.UUID(key_id))
        )
        key = result.scalar_one_or_none()
        if not key:
            raise KeyNotFoundError(f"API key '{key_id}' not found")

        key.is_active = False
        await self.db.commit()

        return {"id": str(key.id), "revoked": True}
