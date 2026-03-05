"""API Keys router — create, list, revoke API keys."""

from fastapi import APIRouter, Depends

from app.api.deps import get_key_service, get_current_key, get_current_key_or_bootstrap
from app.models.api_key import APIKey
from app.schemas.keys import KeyCreate
from app.services.api_key import APIKeyService

router = APIRouter()


@router.post("/keys", status_code=201)
async def create_key(
    body: KeyCreate,
    key_svc: APIKeyService = Depends(get_key_service),
    _key: APIKey | None = Depends(get_current_key_or_bootstrap),
):
    """Create a new API key. The full key is returned once."""
    result = await key_svc.create(name=body.name)
    return {"data": result.model_dump(mode="json")}


@router.get("/keys")
async def list_keys(
    key_svc: APIKeyService = Depends(get_key_service),
    _key: APIKey = Depends(get_current_key),
):
    """List all API keys (prefix + metadata only)."""
    keys = await key_svc.list_all()
    return {"data": [k.model_dump(mode="json") for k in keys]}


@router.delete("/keys/{key_id}")
async def revoke_key(
    key_id: str,
    key_svc: APIKeyService = Depends(get_key_service),
    _key: APIKey = Depends(get_current_key),
):
    """Revoke an API key (soft delete)."""
    result = await key_svc.revoke(key_id)
    return {"data": result}
