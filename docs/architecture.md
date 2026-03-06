# Architecture

## What ModelServe Does

ModelServe lets users on a ROCm GPU machine:

1. Declare which HuggingFace models to serve via environment variables
2. Run `docker compose up` — vLLM downloads and serves each model
3. Get OpenAI-compatible endpoints immediately
4. Manage API keys and users through the dashboard

---

## Services

```text
┌──────────────────────────────────────────────────────────────────┐
│  Docker Compose (ROCm)                                           │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐       │
│  │   Frontend   │   │   Backend    │   │   PostgreSQL   │       │
│  │  Vite/React  │──▶│   FastAPI    │──▶│   (postgres)   │       │
│  │  :3000       │   │  :8000       │   │   :5432        │       │
│  └──────────────┘   └──────────────┘   └────────────────┘       │
│                                                                  │
│  ┌──────────────┐   ┌──────────────┐                             │
│  │   vLLM-1     │   │   vLLM-2     │   (up to 4 slots)          │
│  │  :8081       │   │  :8082       │                             │
│  └──────────────┘   └──────────────┘                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```text
/
├── backend/
│   ├── app/
│   │   ├── main.py               # App factory, lifespan, middleware
│   │   ├── core/
│   │   │   ├── config.py         # Settings via pydantic-settings
│   │   │   ├── database.py       # Async SQLAlchemy engine + session factory
│   │   │   └── security.py       # API key hashing, token generation
│   │   ├── api/
│   │   │   ├── deps.py           # All FastAPI Depends() providers
│   │   │   └── v1/
│   │   │       ├── models.py     # /models router (public model list)
│   │   │       ├── serve.py      # /serve router (authed model list)
│   │   │       ├── keys.py       # /keys router
│   │   │       ├── auth.py       # /auth router
│   │   │       └── health.py     # /health router
│   │   ├── services/
│   │   │   ├── vllm_manager.py   # Config reader + health checker
│   │   │   ├── api_key.py        # Key CRUD logic
│   │   │   └── auth.py           # User auth logic
│   │   ├── models/               # SQLAlchemy ORM models (users, api_keys)
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   └── utils/                # Pure helpers (no side effects)
│   ├── alembic/                  # DB migrations
│   ├── tests/
│   ├── pyproject.toml            # uv managed
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/               # shadcn generated (DO NOT hand-edit)
│   │   │   └── app/              # App-specific composed components
│   │   ├── pages/                # Route-level components
│   │   ├── hooks/                # Custom hooks + TanStack Query hooks
│   │   ├── lib/
│   │   │   ├── api.ts            # API client, base URL config
│   │   │   └── utils.ts          # cn(), formatters
│   │   └── types/                # Shared TypeScript types
│   ├── components.json           # shadcn config
│   └── vite.config.ts
│
├── docker/
│   ├── compose.rocm.yml          # AMD ROCm GPU stack
│   ├── compose.local.yml         # Local dev (no GPU)
│   ├── compose.base.yml          # Shared service config
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── docs/                         # Cross-cutting documentation
│   ├── architecture.md           # This file
│   ├── deployment.md             # Docker, compose, env vars
│   └── api.md                    # API endpoints, auth, response shapes
│
└── README.md                     # User-facing quickstart
```

---

## Data Flow

```text
Admin sets VLLM_MODEL_1=... in .env
  → docker compose --profile vllm-1 up
  → vLLM container pulls model (first run) or loads from cache (subsequent)
  → Backend reads VLLM_MODEL_1 from env, probes http://vllm-1:8080/health
  → GET /models returns { model_id, status: running/loading, endpoint_url }
  → User creates API key via POST /keys
  → User copies endpoint_url + (optional) VLLM_API_KEY
  → User sends inference requests directly to vLLM endpoint
```

---

## What Changed from v0.1.0

| v0.1.0 (old)                        | v0.2.0 (current)                         |
| ----------------------------------- | ---------------------------------------- |
| Docker SDK spawns vLLM containers   | Docker Compose defines vLLM services     |
| Models selected from HuggingFace UI | Models declared via env vars at deploy   |
| `served_models` table tracks state  | Model state is ephemeral (health checks) |
| CUDA + ROCm support planned         | ROCm only (CUDA to be added later)       |
| Dynamic port allocation             | Fixed ports per slot (8081–8084)         |
| Docker socket mounted in backend    | No Docker socket needed                  |
| `docker` Python package required    | Removed — only `httpx` for health checks |
| HuggingFace API browsing            | Removed — models are pre-declared        |
