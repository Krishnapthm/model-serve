"""Serve router — serve and manage vLLM models."""

from fastapi import APIRouter, Depends

from app.api.deps import get_vllm_manager, get_current_user
from app.models.user import User
from app.schemas.serve import ServeCreate
from app.services.vllm_manager import VLLMManager

router = APIRouter()


@router.post("/serve", status_code=202)
async def serve_model(
    body: ServeCreate,
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
):
    """Pull and serve a model via vLLM. Returns 202 Accepted."""
    result = await vllm.serve(
        model_id=body.model_id,
        gpu_type=body.gpu_type,
        owner_id=current_user.id,
    )
    return {"data": result}


@router.get("/serve")
async def list_served(
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
):
    """List all currently served models."""
    models = await vllm.list_served(owner_id=current_user.id)
    return {"data": models}


@router.get("/serve/{served_id}")
async def get_served(
    served_id: str,
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
):
    """Get status of a specific served model. Poll this until status is 'running'."""
    result = await vllm.get_status(served_id, owner_id=current_user.id)
    return {"data": result}


@router.delete("/serve/{served_id}")
async def stop_served(
    served_id: str,
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
):
    """Stop a served model and remove its container."""
    result = await vllm.stop(served_id, owner_id=current_user.id)
    return {"data": result}
