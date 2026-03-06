# ModelServe

A self-hosted model serving platform for AMD ROCm GPUs. Declare the models you want to serve, run `docker compose up`, and get OpenAI-compatible endpoints — no infra knowledge required.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- AMD GPU with ROCm drivers
- [HuggingFace token](https://huggingface.co/settings/tokens) (for gated models)

### Setup

```bash
# Clone
git clone https://github.com/Krishnapthm/model-serve.git && cd model-serve

# Configure environment
cp .env.example .env
# Edit .env — set VLLM_MODEL_1, HF_TOKEN, SECRET_KEY, POSTGRES_PASSWORD

# Start with one model
docker compose -f docker/compose.rocm.yml --profile vllm-1 up --build

# Start with two models
docker compose -f docker/compose.rocm.yml --profile vllm-1 --profile vllm-2 up --build

# Local development (frontend HMR, no GPU/vLLM)
docker compose -f docker/compose.local.yml up --build
```

### First Run vs Subsequent Runs

The **first run** downloads the model weights from HuggingFace into a Docker volume (`hf_cache`). This can take a while depending on model size and network speed.

**Subsequent runs** reuse the cached weights — startup is fast. The cache persists across `docker compose down` / `docker compose up` cycles. Only `docker volume rm` removes it.

### Access

| Service     | URL                                                      |
| ----------- | -------------------------------------------------------- |
| Frontend    | [http://localhost:3000](http://localhost:3000)           |
| Backend API | [http://localhost:8000/docs](http://localhost:8000/docs) |
| vLLM slot 1 | http://localhost:8081/v1                                 |
| vLLM slot 2 | http://localhost:8082/v1                                 |

### Using the Models

Once a model is running (`status: running` in the API), use it like any OpenAI endpoint:

```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mistralai/Mistral-7B-Instruct-v0.3", "messages": [{"role": "user", "content": "Hello!"}]}'
```

Or with the OpenAI Python SDK:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8081/v1",
    api_key="your-vllm-api-key",  # or "dummy" if VLLM_API_KEY is not set
)
response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

## How It Works

1. **Configure** model IDs in `.env` (`VLLM_MODEL_1`, `VLLM_MODEL_2`, etc.)
2. **Start** with `docker compose --profile vllm-1 up`
3. **Wait** — first run downloads the model, subsequent runs use cache
4. **Use** the OpenAI-compatible endpoint directly

## Project Structure

```text
├── backend/          # FastAPI (Python, uv) — see backend/README.md
├── frontend/         # Vite + React + shadcn/ui — see frontend/README.md
├── docker/           # Dockerfiles + Compose files — see docker/README.md
├── docs/             # Cross-cutting docs (architecture, deployment, API)
└── .env.example      # Environment template
```

## Development

### Backend

```bash
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload    # http://localhost:8000
uv run pytest -v --tb=short             # Run tests
```

### Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173
npm run typecheck    # Type check
npm run lint         # Lint
```

## API

Create an account with `POST /api/v1/auth/signup` (or log in with `POST /api/v1/auth/login`) and use the returned bearer token:

`Authorization: Bearer <access_token>`

| Method   | Path                  | Auth | Description                |
| -------- | --------------------- | ---- | -------------------------- |
| `GET`    | `/api/v1/health`      | No   | Health check               |
| `POST`   | `/api/v1/auth/signup` | No   | Signup + token             |
| `POST`   | `/api/v1/auth/login`  | No   | Login + token              |
| `GET`    | `/api/v1/auth/me`     | Yes  | Current user               |
| `GET`    | `/api/v1/models`      | No   | List configured models     |
| `GET`    | `/api/v1/models/{n}`  | No   | Model slot detail          |
| `GET`    | `/api/v1/serve`       | Yes  | List models (authed)       |
| `GET`    | `/api/v1/serve/{n}`   | Yes  | Model slot detail (authed) |
| `POST`   | `/api/v1/keys`        | Yes  | Create API key             |
| `GET`    | `/api/v1/keys`        | Yes  | List keys                  |
| `DELETE` | `/api/v1/keys/{id}`   | Yes  | Revoke key                 |

Full API docs at `http://localhost:8000/docs` when running.

## Stack

FastAPI · PostgreSQL · React · Vite · shadcn/ui · TanStack Query · vLLM (ROCm) · Docker Compose

## Documentation

| Doc                                  | Description                                   |
| ------------------------------------ | --------------------------------------------- |
| [Architecture](docs/architecture.md) | System overview, service diagram, data flow   |
| [Deployment](docs/deployment.md)     | Docker Compose, env vars, GPU setup           |
| [API Reference](docs/api.md)         | Endpoints, auth, response shapes              |
| [Backend](backend/README.md)         | FastAPI setup, DB schema, migrations, testing |
| [Frontend](frontend/README.md)       | React setup, component library, auth flow     |
| [Docker](docker/README.md)           | Compose variants, Dockerfiles, ports          |
