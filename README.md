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
git clone https://github.com/Krishnapthm/model-serve.git && cd model-serve

# Configure environment
cp .env.example .env
# Edit .env — set HF_TOKEN, SECRET_KEY, POSTGRES_PASSWORD (and CORS_* as needed)

# Start (NVIDIA GPU)
docker compose -f docker/compose.cuda.yml up --build

# Start (AMD GPU)
docker compose -f docker/compose.rocm.yml up --build

# Local development (frontend HMR, no GPU/vLLM)
docker compose -f docker/compose.local.yml up --build
```

### Access

| Service     | URL                                                      |
| ----------- | -------------------------------------------------------- |
| Frontend    | [http://localhost:3000](http://localhost:3000)           |
| Backend API | [http://localhost:8000/docs](http://localhost:8000/docs) |

### Deploying on changing public IPs (GPU VPC)

- Frontend API calls auto-resolve to the current browser host on port `8000`, so you do not need to hardcode a fixed public IP.
- Keep `VITE_API_BASE_URL` empty in `.env` unless you intentionally want a custom backend URL.
- Default CORS in `.env.example` is `CORS_ORIGINS=*` (with `CORS_ALLOW_CREDENTIALS=false`) to avoid CORS breaks when the public origin changes.
- For stricter production security, replace `CORS_ORIGINS=*` with a comma-separated allowlist of your exact frontend origins.

## How It Works

1. **Browse** HuggingFace models by category (LLM, Embedding, Image Gen, etc.)
2. **Serve** a model — vLLM pulls and runs it on your GPU
3. **Copy** the `OPENAI_API_KEY` + `OPENAI_BASE_URL` env vars
4. **Use** in any OpenAI SDK client

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

Public endpoints: `GET /api/v1/health`, `GET /api/v1/models`, and `GET /api/v1/models/{model_id}`.

| Method   | Path                  | Description        |
| -------- | --------------------- | ------------------ |
| `GET`    | `/api/v1/health`      | Health check       |
| `POST`   | `/api/v1/auth/signup` | Signup + token     |
| `POST`   | `/api/v1/auth/login`  | Login + token      |
| `GET`    | `/api/v1/auth/me`     | Current user       |
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

## Documentation

| Doc | Description |
| --- | --- |
| [Architecture](docs/architecture.md) | System overview, service diagram, data flow |
| [Deployment](docs/deployment.md) | Docker Compose, env vars, GPU VPC setup |
| [API Reference](docs/api.md) | Endpoints, auth, response shapes |
| [Backend](backend/README.md) | FastAPI setup, DB schema, migrations, testing |
| [Frontend](frontend/README.md) | React setup, component library, auth flow |
| [Docker](docker/README.md) | Compose variants, Dockerfiles, ports |
