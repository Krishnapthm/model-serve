"""FastAPI dependency injection providers."""

from collections.abc import AsyncGenerator

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import verify_key
from app.models.api_key import APIKey
from app.utils.exceptions import InvalidAPIKeyError

from sqlalchemy import select
from datetime import datetime

# Globals set during app lifespan
_session_factory = None
_settings = None

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def init_deps(session_factory, settings: Settings) -> None:
    """Initialize DI globals during app startup.

    Args:
        session_factory: Async session factory from database setup.
        settings: Application settings instance.
    """
    global _session_factory, _settings
    _session_factory = session_factory
    _settings = settings


def get_settings() -> Settings:
    """Provide application settings."""
    return _settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session per request."""
    async with _session_factory() as session:
        yield session


async def get_current_key(
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    """Validate the API key from the X-API-Key header.

    Args:
        api_key: Raw API key from header.
        db: Database session.

    Returns:
        The authenticated APIKey record.

    Raises:
        InvalidAPIKeyError: If key is missing, invalid, or revoked.
    """
    if not api_key:
        raise InvalidAPIKeyError("Missing API key")

    result = await db.execute(select(APIKey).where(APIKey.is_active == True))
    keys = result.scalars().all()

    for key_record in keys:
        if verify_key(api_key, key_record.key_hash):
            key_record.last_used_at = datetime.utcnow()
            await db.commit()
            return key_record

    raise InvalidAPIKeyError("Invalid API key")


async def get_current_key_or_bootstrap(
    api_key: str | None = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> APIKey | None:
    """Allow key bootstrap when no active keys exist.

    Returns:
        The authenticated APIKey record when keys already exist, otherwise None.

    Raises:
        InvalidAPIKeyError: If keys exist and the provided key is invalid.
    """
    result = await db.execute(select(APIKey).where(APIKey.is_active == True).limit(1))
    existing_key = result.scalar_one_or_none()

    if existing_key is None:
        return None

    return await get_current_key(api_key=api_key, db=db)


# --- Service factories ---


def get_hf_service(settings: Settings = Depends(get_settings)):
    """Provide a HuggingFaceService instance."""
    from app.services.huggingface import HuggingFaceService

    return HuggingFaceService(settings)


def get_vllm_manager(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Provide a VLLMManager instance."""
    from app.services.vllm_manager import VLLMManager

    return VLLMManager(db, settings)


def get_key_service(db: AsyncSession = Depends(get_db)):
    """Provide an APIKeyService instance."""
    from app.services.api_key import APIKeyService

    return APIKeyService(db)
