"""Tests for the health endpoint and app creation."""

import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.api.deps import init_deps, get_db
from app.core.config import Settings


@pytest.fixture(autouse=True)
def _init_deps():
    """Ensure DI globals are initialized and DB is mocked for tests."""
    settings = Settings()

    async def mock_db():
        db = AsyncMock()
        db.execute = AsyncMock(
            return_value=AsyncMock(
                scalars=AsyncMock(
                    return_value=AsyncMock(all=AsyncMock(return_value=[]))
                )
            )
        )
        db.commit = AsyncMock()
        yield db

    init_deps(session_factory=None, settings=settings)
    app.dependency_overrides[get_db] = mock_db
    yield
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health():
    """Health endpoint should return 200 with status ok."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_models_is_public():
    """Models endpoint should be accessible without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/models")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_serve_requires_auth():
    """Serve endpoint should return 401 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/serve")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_keys_requires_auth():
    """Keys endpoint should return 401 without API key."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/keys")
    assert resp.status_code == 401
