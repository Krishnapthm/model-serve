# Backend

FastAPI application serving the ModelServe API. Manages user auth, HuggingFace model discovery, vLLM process lifecycle, and API key generation.

## Stack

- **Python 3.12** with **FastAPI**
- **SQLAlchemy 2.x** async ORM (`asyncpg` driver)
- **Alembic** for database migrations
- **Pydantic v2** for request/response validation
- **uv** for dependency management

---

## Getting Started

```bash
cd backend

# Install dependencies
uv sync --dev

# Run the dev server
uv run uvicorn app.main:app --reload    # http://localhost:8000

# Run tests
uv run pytest -v --tb=short
```

> **Always use `uv`** — never `pip install` or `poetry`. The lockfile is `uv.lock` — commit it.

### Adding Dependencies

```bash
uv add fastapi sqlalchemy asyncpg      # Runtime deps
uv add --dev pytest pytest-asyncio httpx  # Dev deps
```

---

## Project Structure

```text
backend/
├── app/
│   ├── main.py               # App factory, lifespan, middleware, exception handlers
│   ├── core/
│   │   ├── config.py         # Settings via pydantic-settings
│   │   ├── database.py       # Async SQLAlchemy engine + session factory
│   │   └── security.py       # API key hashing, JWT token generation
│   ├── api/
│   │   ├── deps.py           # All FastAPI Depends() providers
│   │   └── v1/
│   │       ├── auth.py       # /auth router (signup, login, me)
│   │       ├── health.py     # /health router
│   │       ├── models.py     # /models router
│   │       ├── serve.py      # /serve router
│   │       └── keys.py       # /keys router
│   ├── services/
│   │   ├── auth.py           # User auth logic
│   │   ├── huggingface.py    # HF Hub API client
│   │   ├── vllm_manager.py   # vLLM process lifecycle
│   │   └── api_key.py        # Key CRUD logic
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── base.py           # Declarative base
│   │   ├── user.py           # User model
│   │   ├── api_key.py        # API Key model
│   │   └── served_model.py   # Served Model model
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── keys.py
│   │   ├── models.py
│   │   └── serve.py
│   └── utils/
│       ├── error_codes.py    # Standardized error codes
│       └── exceptions.py     # Domain exception classes
├── alembic/                  # DB migration scripts
│   ├── env.py
│   └── versions/
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── test_routes.py        # Route integration tests
│   └── test_security.py      # Auth/security tests
├── alembic.ini
└── pyproject.toml            # uv-managed project config
```

---

## Database

### Schema

#### `users`

| Column          | Type        | Notes                 |
| --------------- | ----------- | --------------------- |
| `id`            | UUID        | PK                    |
| `email`         | TEXT        | Unique login identity |
| `full_name`     | TEXT        | Nullable display name |
| `password_hash` | TEXT        | bcrypt hash           |
| `created_at`    | TIMESTAMPTZ |                       |
| `is_active`     | BOOLEAN     | Soft disable support  |

#### `api_keys`

| Column         | Type        | Notes                                        |
| -------------- | ----------- | -------------------------------------------- |
| `id`           | UUID        | PK                                           |
| `owner_id`     | UUID        | FK → `users.id`                              |
| `name`         | TEXT        | User-provided label                          |
| `key_hash`     | TEXT        | bcrypt hash — never store plaintext          |
| `key_prefix`   | TEXT        | First 8 chars for display (e.g. `sk-ms_Ab1`) |
| `created_at`   | TIMESTAMPTZ |                                              |
| `last_used_at` | TIMESTAMPTZ | Nullable                                     |
| `is_active`    | BOOLEAN     | Soft delete                                  |

#### `served_models`

| Column         | Type        | Notes                                    |
| -------------- | ----------- | ---------------------------------------- |
| `id`           | UUID        | PK                                       |
| `owner_id`     | UUID        | FK → `users.id`                          |
| `model_id`     | TEXT        | HF model ID                              |
| `display_name` | TEXT        |                                          |
| `pipeline_tag` | TEXT        | e.g. `text-generation`                   |
| `endpoint_url` | TEXT        | Internal vLLM endpoint                   |
| `status`       | ENUM        | `pending`, `running`, `stopped`, `error` |
| `gpu_type`     | ENUM        | `rocm` (schema retains `cuda` for compat) |
| `container_id` | TEXT        | Docker container ID                      |
| `started_at`   | TIMESTAMPTZ |                                          |
| `stopped_at`   | TIMESTAMPTZ | Nullable                                 |

### Migrations

```bash
# Create a new migration after changing ORM models
uv run alembic revision --autogenerate -m "add_served_models_table"

# Apply locally
uv run alembic upgrade head

# Rollback one step
uv run alembic downgrade -1
```

On `docker compose up`, the backend entrypoint runs `alembic upgrade head` automatically — no manual migration step needed.

### Connection String

```
postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}
```

In Docker Compose, `host` is the service name `db`. In local dev (outside Docker), use `localhost`.

---

## Testing

```bash
uv run pytest -v --tb=short
```

- Uses `pytest-asyncio` with `asyncio_mode = "auto"` (configured in `pyproject.toml`).
- Route tests use `httpx.AsyncClient` + `ASGITransport` — never `TestClient`.
- External calls (HF Hub, vLLM) are mocked at the service boundary.
- Fixtures live in `tests/conftest.py`.
