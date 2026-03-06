"""Serve router — list configured vLLM model slots and their status."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_vllm_manager, get_current_user
from app.models.user import User
from app.services.vllm_manager import VLLMManager

router = APIRouter()


@router.get("/serve")
async def list_served(
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
):
    """List all configured model slots and their live status."""
    models = await vllm.list_models()
    return {"data": models}


@router.get("/serve/{slot}")
async def get_served(
    slot: int,
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
):
    """Get a specific model slot. Poll until status is 'running'."""
    result = await vllm.get_model(slot)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Model slot {slot} is not configured")
    return {"data": result}
