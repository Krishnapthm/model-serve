"""API key generation, hashing, and verification."""

from datetime import datetime, timedelta, timezone
import secrets

import bcrypt
import jwt
from jwt import InvalidTokenError

API_KEY_PREFIX = "sk-ms_"
API_KEY_BYTES = 32  # 32 random bytes → 43 base64 chars
JWT_ALGORITHM = "HS256"


def generate_api_key() -> str:
    """Generate a new API key with the sk-ms_ prefix.

    Returns:
        Full API key string (shown to user once).
    """
    random_part = secrets.token_urlsafe(API_KEY_BYTES)
    return f"{API_KEY_PREFIX}{random_part}"


def hash_key(raw_key: str) -> str:
    """Bcrypt-hash an API key for storage.

    Args:
        raw_key: The full plaintext API key.

    Returns:
        Bcrypt hash string.
    """
    return bcrypt.hashpw(raw_key.encode(), bcrypt.gensalt()).decode()


def verify_key(raw_key: str, hashed: str) -> bool:
    """Verify a plaintext key against its bcrypt hash.

    Args:
        raw_key: The full plaintext API key.
        hashed: The stored bcrypt hash.

    Returns:
        True if the key matches.
    """
    return bcrypt.checkpw(raw_key.encode(), hashed.encode())


def extract_prefix(raw_key: str) -> str:
    """Extract the display prefix from an API key.

    Args:
        raw_key: The full plaintext API key.

    Returns:
        First 12 characters for display (e.g. ``sk-ms_Ab1C``).
    """
    return raw_key[:12]


def hash_password(password: str) -> str:
    """Bcrypt-hash a plaintext password.

    Args:
        password: Plaintext user password.

    Returns:
        Bcrypt hash string.
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a bcrypt hash.

    Args:
        password: Plaintext password from login request.
        password_hash: Stored bcrypt hash.

    Returns:
        True when the password matches the hash.
    """
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def create_access_token(
    *,
    subject: str,
    secret_key: str,
    expires_minutes: int,
) -> str:
    """Create a signed JWT access token.

    Args:
        subject: Token subject, typically the user ID.
        secret_key: Application signing secret.
        expires_minutes: Token lifetime in minutes.

    Returns:
        Encoded JWT token string.
    """
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str, secret_key: str) -> dict:
    """Decode and validate a JWT access token.

    Args:
        token: Encoded JWT token.
        secret_key: Application signing secret.

    Returns:
        Decoded payload dict.

    Raises:
        ValueError: If the token is invalid or missing a string subject.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[JWT_ALGORITHM])
    except InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not subject:
        raise ValueError("Invalid token payload")

    return payload
