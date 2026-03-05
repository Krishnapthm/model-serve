"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check — no authentication required."""
    return {"status": "ok"}
