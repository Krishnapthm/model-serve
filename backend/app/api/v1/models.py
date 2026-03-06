"""Models router — list configured vLLM models (public)."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_vllm_manager
from app.services.vllm_manager import VLLMManager

router = APIRouter()


@router.get("/models")
async def list_models(
    vllm: VLLMManager = Depends(get_vllm_manager),
):
    """List configured models and their live health status (public)."""
    models = await vllm.list_models()
    return {"data": models}


@router.get("/models/{slot}")
async def get_model(
    slot: int,
    vllm: VLLMManager = Depends(get_vllm_manager),
):
    """Get a single model slot by number."""
    model = await vllm.get_model(slot)
    if model is None:
        raise HTTPException(status_code=404, detail=f"Model slot {slot} is not configured")
    return {"data": model}
