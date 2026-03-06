# model-serve

> Set a model ID. Run one command. Get an OpenAI-compatible endpoint.

model-serve is a self-hosted LLM serving platform powered by vLLM. No infra expertise required — just drop a Hugging Face token and model ID into your `.env`, run `docker compose up`, and you're serving.

---

## Why model-serve?

Most self-hosted LLM setups require deep knowledge of GPU drivers, inference runtimes, and container orchestration. model-serve collapses all of that into a single `docker compose` command. Your existing OpenAI-based code works without modification.

---

## Quickstart

**Prerequisites:** Docker & Docker Compose, a GPU with drivers installed, a [Hugging Face token](https://huggingface.co/settings/tokens)

```bash
# 1. Clone
git clone https://github.com/Krishnapthm/model-serve.git && cd model-serve

# 2. Configure
cp .env.example .env
# Edit .env — set VLLM_MODEL_1, HF_TOKEN, SECRET_KEY, POSTGRES_PASSWORD

# 3. Serve
docker compose -f docker/compose.rocm.yml --env-file .env --profile vllm-1 up --build
```

That's it. Your model is live at `http://localhost:8081/v1`.

> **First run** downloads model weights from Hugging Face into a persistent Docker volume. Subsequent runs reuse the cache. The cache survives `docker compose down` / `up` cycles. Only `docker volume rm` / `docker compose down -b` clears it.

---

## Use it like OpenAI

Once running, hit it with any OpenAI compatible client:

```bash
curl http://localhost:8081/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mistralai/Mistral-7B-Instruct-v0.3",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8081/v1", api_key="your-key")
response = client.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    messages=[{"role": "user", "content": "Hello!"}],
)
```

---

## Serving multiple models

Add more profiles to serve up to two models simultaneously:

```bash
docker compose -f docker/compose.rocm.yml --env-file .env \
  --profile vllm-1 --profile vllm-2 up --build
```

| Slot | Endpoint |
|------|----------|
| Model 1 | `http://localhost:8081/v1` |
| Model 2 | `http://localhost:8082/v1` |

---

## What's included

| Service | URL |
|---------|-----|
| Frontend dashboard | `http://localhost:3000` |
| Backend API + docs | `http://localhost:8000/docs` |
| vLLM slot 1 | `http://localhost:8081/v1` |
| vLLM slot 2 | `http://localhost:8082/v1` |

The **frontend** gives you a live view of model status and lets you manage API keys. The **backend** handles auth, key management, and proxies health/status from vLLM.

---

## Local development (no GPU)

```bash
docker compose -f docker/compose.local.yml up --build
```

Spins up the full stack with frontend hot-module reloading no GPU or vLLM required. Great for working on the UI or backend.

---

## Project structure

```
├── backend/        # FastAPI (Python, uv)
├── frontend/       # Vite + React + shadcn/ui
├── docker/         # Dockerfiles + Compose files
├── docs/           # Architecture, deployment, API reference
└── .env.example    # Start here
```

---

## API reference

Authenticate with `POST /api/v1/auth/signup` or `POST /api/v1/auth/login`, then pass the returned token as `Authorization: Bearer <token>`.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/v1/health` | No | Health check |
| `POST` | `/api/v1/auth/signup` | No | Create account + get token |
| `POST` | `/api/v1/auth/login` | No | Login + get token |
| `GET` | `/api/v1/models` | No | List configured model slots |
| `GET` | `/api/v1/serve` | Yes | List running models |
| `POST` | `/api/v1/keys` | Yes | Create API key |
| `GET` | `/api/v1/keys` | Yes | List API keys |
| `DELETE` | `/api/v1/keys/{id}` | Yes | Revoke API key |

Full interactive docs at `http://localhost:8000/docs` when running.

---

## Documentation

| Doc | Description |
|-----|-------------|
| [Architecture](docs/architecture.md) | System overview, service diagram, data flow |
| [Deployment](docs/deployment.md) | Docker Compose variants, env vars, GPU setup |
| [API Reference](docs/api.md) | Endpoints, auth, response shapes |
| [Backend](backend/README.md) | FastAPI setup, DB schema, migrations, testing |
| [Frontend](frontend/README.md) | React setup, component library, auth flow |
| [Docker](docker/README.md) | Compose variants, Dockerfiles, ports |

---

## Stack

**Inference:** vLLM · **Backend:** FastAPI · PostgreSQL · **Frontend:** React · Vite · shadcn/ui · TanStack Query · **Infrastructure:** Docker Compose
