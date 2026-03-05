"""Shared test fixtures."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def mock_db():
    """Provide a mock async database session."""
    db = AsyncMock()
    db.execute = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.add = MagicMock()
    return db
