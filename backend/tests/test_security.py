"""Tests for the security module."""

from app.core.security import generate_api_key, hash_key, verify_key, extract_prefix


def test_generate_api_key_format():
    """Generated key should have sk-ms_ prefix."""
    key = generate_api_key()
    assert key.startswith("sk-ms_")
    assert len(key) > 20


def test_hash_and_verify():
    """Hashed key should verify against original."""
    key = generate_api_key()
    hashed = hash_key(key)
    assert verify_key(key, hashed)
    assert not verify_key("wrong-key", hashed)


def test_extract_prefix():
    """Prefix should be first 12 chars."""
    key = "sk-ms_AbCdEfGhIjKl"
    assert extract_prefix(key) == "sk-ms_AbCdEf"
