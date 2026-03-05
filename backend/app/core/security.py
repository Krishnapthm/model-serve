"""API key generation, hashing, and verification."""

import secrets
import bcrypt

API_KEY_PREFIX = "sk-ms_"
API_KEY_BYTES = 32  # 32 random bytes → 43 base64 chars


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
