# Architecture

## What This Project Does

ModelServe lets users on a GPU VM:

1. Create an account / log in (email + password)
2. Browse available HuggingFace models (categorized by type)
3. Click **Serve** → backend pulls the model and launches a vLLM process
4. Get an OpenAI-compatible endpoint immediately
5. Use a generated API key (`OPENAI_API_KEY` + `OPENAI_BASE_URL`) in any OpenAI SDK client

---

## Services

```text
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

```text
User clicks "Serve"
  → POST /api/v1/serve  { model_id, hf_token }
  → vllm_manager.py: docker run vllm/vllm-openai ... --model {model_id}
  → Returns { endpoint_url, api_key }
  → Frontend displays env var snippet for user to copy
```

---

## Model Categories

Models are categorized by HuggingFace pipeline tag:

| HF Pipeline Tag                | Display Label    | Badge Color |
| ------------------------------ | ---------------- | ----------- |
| `text-generation`              | LLM              | blue        |
| `feature-extraction`           | Text Embedding   | purple      |
| `text-to-image`                | Image Generation | pink        |
| `text-to-video`                | Video Generation | orange      |
| `automatic-speech-recognition` | Speech-to-Text   | green       |
| `image-to-text`                | Vision-Language  | cyan        |
| custom                         | Custom           | gray        |

---

## Environment Variables

| Variable                 | Service       | Description                                      |
| ------------------------ | ------------- | ------------------------------------------------ |
| `HF_TOKEN`               | backend       | HuggingFace read token                           |
| `DATABASE_URL`           | backend       | `postgresql+asyncpg://...`                       |
| `SECRET_KEY`             | backend       | Used for API key signing                         |
| `CORS_ORIGINS`           | backend       | CORS allowlist (`*` or CSV list)                 |
| `CORS_ALLOW_CREDENTIALS` | backend       | CORS credentials flag (must be `false` with `*`) |
| `CORS_ORIGIN_REGEX`      | backend       | Optional CORS regex matcher                      |
| `VLLM_HOST`              | backend       | vLLM sidecar hostname                            |
| `VITE_API_BASE_URL`      | frontend      | Optional backend base URL override               |
| `OPENAI_API_KEY`         | client (user) | Generated API key                                |
| `OPENAI_BASE_URL`        | client (user) | Served model endpoint                            |
