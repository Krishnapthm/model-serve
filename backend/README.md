# Backend

FastAPI application serving the ModelServe API. Manages user auth, API key generation, and reads vLLM model configuration from environment.

## Stack

- **Python 3.12** with **FastAPI**
- **SQLAlchemy 2.x** async ORM (`asyncpg` driver)
- **Alembic** for database migrations
- **Pydantic v2** for request/response validation
- **httpx** for vLLM health checks
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
│   │       ├── models.py     # /models router (configured model slots)
│   │       ├── serve.py      # /serve router (authed model listing)
│   │       └── keys.py       # /keys router
│   ├── services/
│   │   ├── auth.py           # User auth logic
│   │   ├── vllm_manager.py   # vLLM config reader + health checker
│   │   └── api_key.py        # Key CRUD logic
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── base.py           # Declarative base
│   │   ├── user.py           # User model
│   │   └── api_key.py        # API Key model
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── common.py
│   │   ├── keys.py
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

## Key Concepts

### Model Configuration

Models are **not** managed via the API. They are declared at deploy time through environment variables:

```env
VLLM_MODEL_1=mistralai/Mistral-7B-Instruct-v0.3
VLLM_MODEL_2=meta-llama/Llama-3-8B
VLLM_MODEL_3=
VLLM_MODEL_4=
```

The backend reads these settings and provides:

- `GET /models` — public list of configured models with live health status
- `GET /serve` — same list, but requires bearer auth

The `VLLMManager` service probes each vLLM instance's `/health` endpoint to determine whether a model is `running` or still `loading`.

### API Keys

API keys are managed through the dashboard (bearer auth required):

- `POST /keys` — create a new key (plaintext returned once)
- `GET /keys` — list keys (prefix + metadata only)
- `DELETE /keys/{id}` — revoke a key

Keys are stored as bcrypt hashes. The `sk-ms_` prefix identifies ModelServe keys.

### Auth Flow

Users sign up / log in via email + password. The backend returns a JWT bearer token used for all authenticated endpoints (keys, serve listing).

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

| Column         | Type        | Notes                                         |
| -------------- | ----------- | --------------------------------------------- |
| `id`           | UUID        | PK                                            |
| `owner_id`     | UUID        | FK → `users.id`                               |
| `name`         | TEXT        | User-provided label                           |
| `key_hash`     | TEXT        | bcrypt hash — never store plaintext           |
| `key_prefix`   | TEXT        | First 12 chars for display (e.g. `sk-ms_Ab1`) |
| `created_at`   | TIMESTAMPTZ |                                               |
| `last_used_at` | TIMESTAMPTZ | Nullable                                      |
| `is_active`    | BOOLEAN     | Soft delete                                   |

> **Note:** The `served_models` table from v0.1.0 has been dropped. Model state is now ephemeral — determined by environment config + live health checks.

### Migrations

```bash
# Create a new migration after changing ORM models
uv run alembic revision --autogenerate -m "description"

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
- vLLM health checks are not mocked — they simply fail (model status = `loading`) when no real vLLM is running.
- Fixtures live in `tests/conftest.py`.
