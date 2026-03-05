"""Models router — browse HuggingFace models."""

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_hf_service
from app.services.huggingface import HuggingFaceService

router = APIRouter()


@router.get("/models")
async def list_models(
    category: str | None = Query(None, description="Filter by pipeline tag"),
    q: str | None = Query(None, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    hf_svc: HuggingFaceService = Depends(get_hf_service),
):
    """List HuggingFace models with optional category filter and search."""
    models, total = await hf_svc.list_models(
        category=category, query=q, page=page, page_size=page_size
    )
    return {
        "data": [m.model_dump() for m in models],
        "meta": {"page": page, "page_size": page_size, "total": total},
    }


@router.get("/models/{model_id:path}")
async def get_model(
    model_id: str,
    hf_svc: HuggingFaceService = Depends(get_hf_service),
):
    """Get detailed info for a single model."""
    model = await hf_svc.get_model(model_id)
    return {"data": model.model_dump()}
