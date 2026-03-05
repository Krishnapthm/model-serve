# Database

## Stack

- **PostgreSQL 16** via Docker
- **SQLAlchemy 2.x** async ORM (`sqlalchemy[asyncio]` + `asyncpg`)
- **Alembic** for migrations

---

## Schema Overview

### `api_keys`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `name` | TEXT | User-provided label |
| `key_hash` | TEXT | bcrypt hash — never store plaintext |
| `key_prefix` | TEXT | First 8 chars for display (e.g. `sk-ms_Ab1`) |
| `created_at` | TIMESTAMPTZ | |
| `last_used_at` | TIMESTAMPTZ | Nullable |
| `is_active` | BOOLEAN | Soft delete |

### `served_models`

| Column | Type | Notes |
|---|---|---|
| `id` | UUID | PK |
| `model_id` | TEXT | HF model ID |
| `display_name` | TEXT | |
| `pipeline_tag` | TEXT | e.g. `text-generation` |
| `endpoint_url` | TEXT | Internal vLLM endpoint |
| `status` | ENUM | `pending`, `running`, `stopped`, `error` |
| `gpu_type` | ENUM | `cuda`, `rocm` |
| `container_id` | TEXT | Docker container ID |
| `started_at` | TIMESTAMPTZ | |
| `stopped_at` | TIMESTAMPTZ | Nullable |

---

## Migrations Workflow

```bash
# Create a new migration after changing ORM models
cd backend
uv run alembic revision --autogenerate -m "add_served_models_table"

# Apply locally
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1
```

**On `docker compose up`**, the backend entrypoint runs `alembic upgrade head` automatically.
New team members and CI never need to run migrations manually.

---

## Session Usage

Always use the injected session from `deps.py`. Never create a session manually in a service or router.

```python
# Correct — session injected via DI
async def get_api_keys(db: AsyncSession = Depends(get_db)) -> list[APIKey]:
    result = await db.execute(select(APIKeyModel).where(APIKeyModel.is_active == True))
    return result.scalars().all()
```

Use `db.execute()` with explicit `select()` statements. Avoid ORM lazy loading — always eager-load relationships with `selectinload` or `joinedload`.

---

## Connection String

```
postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}
```

In Docker Compose, `host` is the service name: `db`.
In local dev (outside Docker), use `localhost`.
