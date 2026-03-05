# Architecture

## What This Project Does

ModelServe lets users on a GPU VM:
1. Enter a HuggingFace token → browse available models (categorized by type)
2. Click **Serve** → backend pulls the model and launches a vLLM process
3. Get an OpenAI-compatible endpoint immediately
4. Use a single API key (`OPENAI_API_KEY` + `OPENAI_BASE_URL`) in any OpenAI SDK client

---

## Services

```
┌─────────────────────────────────────────────────────────────┐
│  Docker Compose (cuda or rocm)                              │
│                                                             │
│  ┌──────────────┐   ┌──────────────┐   ┌────────────────┐  │
│  │   Frontend   │   │   Backend    │   │   PostgreSQL   │  │
│  │  Vite/React  │──▶│   FastAPI    │──▶│   (postgres)   │  │
│  │  :3000       │   │  :8000       │   │   :5432        │  │
│  └──────────────┘   └──────┬───────┘   └────────────────┘  │
│                            │                                │
│                     ┌──────▼───────┐                        │
│                     │  vLLM sidecar│                        │
│                     │  (spawned    │                        │
│                     │   per model) │                        │
│                     └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
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
│   │   │       ├── models.py     # /models router
│   │   │       ├── serve.py      # /serve router
│   │   │       └── keys.py       # /keys router
│   │   ├── services/
│   │   │   ├── huggingface.py    # HF Hub API client
│   │   │   ├── vllm_manager.py   # vLLM process lifecycle
│   │   │   └── api_key.py        # Key CRUD logic
│   │   ├── models/               # SQLAlchemy ORM models
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
│   │   │   ├── api.ts            # axios/fetch client, base URL config
│   │   │   └── utils.ts          # cn(), formatters
│   │   └── types/                # Shared TypeScript types
│   ├── components.json           # shadcn config
│   └── vite.config.ts
│
├── docker/
│   ├── compose.cuda.yml          # NVIDIA GPU stack
│   ├── compose.rocm.yml          # AMD GPU stack
│   ├── backend.Dockerfile
│   └── frontend.Dockerfile
│
├── agent_docs/                   # This folder
└── README.md
```

---

## Data Flow: Serving a Model

```
User clicks "Serve"
  → POST /api/v1/serve  { model_id, hf_token }
  → vllm_manager.py: docker run vllm/vllm-openai ... --model {model_id}
  → Returns { endpoint_url, api_key }
  → Frontend displays env var snippet for user to copy
```

---

## Model Categories

Models are categorized by HuggingFace pipeline tag:

| HF Pipeline Tag | Display Label | Badge Color |
|---|---|---|
| `text-generation` | LLM | blue |
| `feature-extraction` | Text Embedding | purple |
| `text-to-image` | Image Generation | pink |
| `text-to-video` | Video Generation | orange |
| `automatic-speech-recognition` | Speech-to-Text | green |
| `image-to-text` | Vision-Language | cyan |
| custom | Custom | gray |

---

## Environment Variables

| Variable | Service | Description |
|---|---|---|
| `HF_TOKEN` | backend | HuggingFace read token |
| `DATABASE_URL` | backend | `postgresql+asyncpg://...` |
| `SECRET_KEY` | backend | Used for API key signing |
| `VLLM_HOST` | backend | vLLM sidecar hostname |
| `VITE_API_BASE_URL` | frontend | Backend base URL |
| `OPENAI_API_KEY` | client (user) | Generated API key |
| `OPENAI_BASE_URL` | client (user) | Served model endpoint |
