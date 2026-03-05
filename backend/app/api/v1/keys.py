"""API Keys router — create, list, revoke API keys."""

from fastapi import APIRouter, Depends

from app.api.deps import get_key_service, get_current_user
from app.models.user import User
from app.schemas.keys import KeyCreate
from app.services.api_key import APIKeyService

router = APIRouter()


@router.post("/keys", status_code=201)
async def create_key(
    body: KeyCreate,
    key_svc: APIKeyService = Depends(get_key_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new API key. The full key is returned once."""
    result = await key_svc.create(name=body.name, owner_id=current_user.id)
    return {"data": result.model_dump(mode="json")}


@router.get("/keys")
async def list_keys(
    key_svc: APIKeyService = Depends(get_key_service),
    current_user: User = Depends(get_current_user),
):
    """List all API keys (prefix + metadata only)."""
    keys = await key_svc.list_all(owner_id=current_user.id)
    return {"data": [k.model_dump(mode="json") for k in keys]}


@router.delete("/keys/{key_id}")
async def revoke_key(
    key_id: str,
    key_svc: APIKeyService = Depends(get_key_service),
    current_user: User = Depends(get_current_user),
):
    """Revoke an API key (soft delete)."""
    result = await key_svc.revoke(key_id, owner_id=current_user.id)
    return {"data": result}
