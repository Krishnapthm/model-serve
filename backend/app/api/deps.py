"""FastAPI dependency injection providers."""

from collections.abc import AsyncGenerator
import uuid

from fastapi import Depends, Security
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import decode_access_token, verify_key
from app.models.api_key import APIKey
from app.models.user import User
from app.utils.exceptions import InvalidAPIKeyError, InvalidAuthTokenError

from sqlalchemy import select
from datetime import datetime

# Globals set during app lifespan
_session_factory = None
_settings = None

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_header = HTTPBearer(auto_error=False)


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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_header),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """Validate and resolve the current user from bearer auth.

    Args:
        credentials: Authorization header credentials.
        db: Database session.
        settings: App settings for token secret and expiry config.

    Returns:
        Authenticated user record.

    Raises:
        InvalidAuthTokenError: If the token is missing, invalid, or user is not found.
    """
    if credentials is None:
        raise InvalidAuthTokenError("Missing bearer token")

    try:
        payload = decode_access_token(credentials.credentials, settings.secret_key)
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError):
        raise InvalidAuthTokenError("Invalid bearer token")

    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise InvalidAuthTokenError("Invalid bearer token")

    return user


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


def get_auth_service(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    """Provide an AuthService instance."""
    from app.services.auth import AuthService

    return AuthService(db, settings)
