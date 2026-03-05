# ModelServe

A self-hosted GPU model serving platform. Browse HuggingFace models, click **Serve**, and get an OpenAI-compatible endpoint — no infra knowledge required.

## Quick Start

### Prerequisites

- Docker & Docker Compose
- GPU with NVIDIA (CUDA) or AMD (ROCm) drivers
- [HuggingFace token](https://huggingface.co/settings/tokens)

### Setup

```bash
# Clone
git clone https://github.com/your-org/modelserve && cd modelserve

# Configure environment
cp .env.example .env
# Edit .env — set HF_TOKEN, SECRET_KEY, POSTGRES_PASSWORD

# Start (NVIDIA GPU)
docker compose -f docker/compose.cuda.yml up --build

# Start (AMD GPU)
docker compose -f docker/compose.rocm.yml up --build
```

### Access

| Service     | URL                                                      |
| ----------- | -------------------------------------------------------- |
| Frontend    | [http://localhost:3000](http://localhost:3000)           |
| Backend API | [http://localhost:8000/docs](http://localhost:8000/docs) |

## How It Works

1. **Browse** HuggingFace models by category (LLM, Embedding, Image Gen, etc.)
2. **Serve** a model — vLLM pulls and runs it on your GPU
3. **Copy** the `OPENAI_API_KEY` + `OPENAI_BASE_URL` env vars
4. **Use** in any OpenAI SDK client

## Project Structure

```
├── backend/          # FastAPI (Python, uv)
├── frontend/         # Vite + React + shadcn/ui
├── docker/           # Dockerfiles + Compose files
├── agent_docs/       # Agent reference docs
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

Most endpoints require an API key in the `X-API-Key` header.
Public endpoints: `GET /api/v1/health`, `GET /api/v1/models`, and `GET /api/v1/models/{model_id}`.
When the system has no active keys yet, the first `POST /api/v1/keys` request is allowed without auth to bootstrap access.

| Method   | Path                  | Description        |
| -------- | --------------------- | ------------------ |
| `GET`    | `/api/v1/health`      | Health check       |
| `GET`    | `/api/v1/models`      | List HF models     |
| `GET`    | `/api/v1/models/{id}` | Model detail       |
| `POST`   | `/api/v1/serve`       | Serve a model      |
| `GET`    | `/api/v1/serve`       | List served models |
| `DELETE` | `/api/v1/serve/{id}`  | Stop a model       |
| `POST`   | `/api/v1/keys`        | Create API key     |
| `GET`    | `/api/v1/keys`        | List keys          |
| `DELETE` | `/api/v1/keys/{id}`   | Revoke key         |

Full API docs at `http://localhost:8000/docs` when running.

## Stack

FastAPI · PostgreSQL · React · Vite · shadcn/ui · TanStack Query · vLLM · Docker Compose
