---
name: 'Backend Conventions'
description: 'FastAPI patterns: dependency injection, service layer, schemas, error handling, testing, and database session usage'
applyTo: 'backend/**'
---

# Backend Coding Conventions

## Dependency Injection

All shared resources (DB session, services, current user/API key) live in `app/api/deps.py`.
Routers import **only** from `deps.py` — never directly from services or DB modules.

```python
# app/api/deps.py — canonical providers
async def get_db() -> AsyncGenerator[AsyncSession, None]: ...
async def get_hf_service(db = Depends(get_db)) -> HuggingFaceService: ...
async def get_current_key(api_key = Security(api_key_header), db = Depends(get_db)) -> APIKey: ...
async def get_current_user(credentials = Security(bearer_header), db = Depends(get_db), settings = Depends(get_settings)) -> User: ...
```

```python
# ✅ Correct — router uses DI
@router.get("/serve")
async def list_models(
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return await vllm.list_served(owner_id=current_user.id)
```

For dashboard auth, use JWT bearer tokens (`Authorization: Bearer ...`) and resolve identity via `get_current_user`. Never decode tokens directly in routers.

## Service Layer

- One file per domain in `app/services/`.
- Services receive dependencies via `__init__` — never import globals.
- Services are the **only** layer allowed to hit external APIs or the DB.
- Routers call services. Services do not call other services directly — compose via the DI graph.

```python
class HuggingFaceService:
    """Wraps the HuggingFace Hub API for model discovery."""

    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings
```

## Docstrings — Google Style

Every public function and class gets a docstring:

```python
async def serve_model(model_id: str, gpu_type: GPUType) -> ServedModel:
    """Launch a vLLM server for the given model.

    Args:
        model_id: HuggingFace model ID (e.g. ``mistralai/Mistral-7B-Instruct-v0.2``).
        gpu_type: Target GPU backend — ``cuda`` or ``rocm``.

    Returns:
        A ``ServedModel`` with endpoint URL and generated API key.

    Raises:
        ModelPullError: If the model cannot be pulled from HuggingFace.
        GPUUnavailableError: If no GPU is available on the host.
    """
```

## Pydantic Schemas

- `schemas/` contains **only** Pydantic models. No ORM imports.
- Naming: `ModelRead`, `ModelCreate`, `ModelUpdate` — never generic `ModelIn`/`ModelOut`.
- Always set `model_config = ConfigDict(from_attributes=True)` on read schemas.

## Error Handling

- Define domain exceptions in `app/utils/exceptions.py`.
- Register exception handlers in `main.py`.
- **Never** raise `HTTPException` inside services — only in routers or exception handlers.

```python
# utils/exceptions.py
class ModelNotFoundError(Exception):
    """Raised when a requested model does not exist on HuggingFace."""
```

## Response Shape

Success responses: `{ "data": {...}, "meta": {...} }`
Error responses: `{ "detail": "...", "code": "ERROR_CODE" }`
Error codes are defined in `app/utils/error_codes.py`.

## Database Sessions

Always use the injected session from `deps.py`. Never create sessions manually.

```python
# ✅ Correct — session via DI
async def get_api_keys(db: AsyncSession = Depends(get_db)) -> list[APIKey]:
    result = await db.execute(select(APIKeyModel).where(APIKeyModel.is_active == True))
    return result.scalars().all()
```

Use `db.execute()` with explicit `select()` statements. Avoid ORM lazy loading — always eager-load relationships with `selectinload` or `joinedload`.

## Testing

- `pytest-asyncio` with `asyncio_mode = "auto"`.
- Use `httpx.AsyncClient` + `ASGITransport` for route tests — never `TestClient`.
- Mock external calls (HF Hub, vLLM) at the service boundary.
- Fixtures live in `tests/conftest.py`.

## Package Management

Use **uv** exclusively. Never `pip install` or `poetry`.

```bash
uv add <package>            # runtime dep
uv add --dev <package>      # dev dep
uv run pytest               # run anything
```
