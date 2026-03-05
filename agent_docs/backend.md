# Backend Conventions

## Package Management — uv (mandatory)

```bash
# Install deps
uv add fastapi sqlalchemy asyncpg

# Add dev dep
uv add --dev pytest pytest-asyncio httpx

# Run anything
uv run pytest
uv run uvicorn app.main:app --reload
```

Never use `pip install` or `poetry`. The lockfile is `uv.lock` — commit it.

---

## Dependency Injection Pattern

All shared resources (DB session, services, current user/API key) live in `app/api/deps.py`.
Routers import only from `deps.py` — never directly from services or DB.

```python
# app/api/deps.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_hf_service(db: AsyncSession = Depends(get_db)) -> HuggingFaceService:
    return HuggingFaceService(db)

async def get_current_key(
    api_key: str = Security(api_key_header),
    db: AsyncSession = Depends(get_db),
) -> APIKey:
    ...

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_header),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    ...
```

```python
# app/api/v1/models.py  ✅ correct
@router.get("/serve")
async def list_models(
    vllm: VLLMManager = Depends(get_vllm_manager),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    return await vllm.list_served(owner_id=current_user.id)
```

For dashboard auth, use JWT bearer tokens (`Authorization: Bearer ...`) and resolve identity via `get_current_user`. Do not decode tokens directly in routers.

---

## Service Layer Rules

- Services live in `app/services/`. One file per domain.
- Services receive dependencies via `__init__` — never import globals.
- Services are the only layer allowed to hit external APIs or the DB.
- Routers call services. Services do not call other services directly — use the DI graph.

```python
class HuggingFaceService:
    """Wraps the HuggingFace Hub API for model discovery."""

    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {settings.hf_token}"}
        )

    async def list_models(self, category: str | None = None) -> list[ModelSummary]:
        """Fetch and cache models from HF Hub, optionally filtered by pipeline tag."""
        ...
```

---

## Docstring Style

Every public function and class gets a docstring. Use Google-style.

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

---

## Schema Conventions

- `schemas/` contains only Pydantic models. No ORM imports.
- Naming: `ModelRead`, `ModelCreate`, `ModelUpdate` — never generic `ModelIn`/`ModelOut`.
- Always set `model_config = ConfigDict(from_attributes=True)` on read schemas.

---

## Error Handling

Define domain exceptions in `app/utils/exceptions.py`. Register handlers in `main.py`.

```python
# utils/exceptions.py
class ModelNotFoundError(Exception):
    """Raised when a requested model does not exist on HuggingFace."""

# main.py
@app.exception_handler(ModelNotFoundError)
async def model_not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": str(exc)})
```

Never raise `HTTPException` inside services — only in routers or exception handlers.

---

## Testing

- Use `pytest-asyncio` with `asyncio_mode = "auto"` in `pyproject.toml`.
- Use `httpx.AsyncClient` + `ASGITransport` for route tests — never `TestClient`.
- Mock external calls (HF Hub, vLLM) at the service boundary.
- Fixtures live in `tests/conftest.py`.

```bash
uv run pytest -v --tb=short
```

---

## Database Initialization

The DB schema is applied automatically on `docker compose up` via an Alembic `upgrade head` entrypoint script in the backend Dockerfile. There is no manual migration step for users.

See `agent_docs/database.md` for schema details and migration workflow.
