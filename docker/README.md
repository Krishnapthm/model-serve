# Docker

Docker Compose setup for ModelServe. Provides GPU-accelerated (CUDA/ROCm) and local development configurations.

---

## Compose Files

| File               | Purpose                                         |
| ------------------ | ----------------------------------------------- |
| `compose.base.yml` | Shared service config — extended by other files |
| `compose.cuda.yml` | NVIDIA GPU stack (`nvidia` runtime)             |
| `compose.rocm.yml` | AMD GPU stack (`/dev/kfd` + `/dev/dri`)         |
| `compose.local.yml`| Local dev — DB + backend + frontend HMR, no GPU |

---

## Quickstart

```bash
# From repo root:

# NVIDIA
docker compose -f docker/compose.cuda.yml up --build

# AMD
docker compose -f docker/compose.rocm.yml up --build

# Local development (no GPU)
docker compose -f docker/compose.local.yml up --build
```

---

## Service Topology

```yaml
services:
  db:          # PostgreSQL 16 — healthcheck enabled
  backend:     # FastAPI — depends on db, runs migrations on start
  frontend:    # Vite/React — serves on :3000
  vllm:        # vLLM OpenAI-compatible server (GPU stacks only)
```

### CUDA-specific Config

```yaml
backend:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]

vllm:
  image: vllm/vllm-openai:latest
  runtime: nvidia
```

### ROCm-specific Config

```yaml
vllm:
  image: vllm/vllm-openai:rocm
  devices:
    - /dev/kfd
    - /dev/dri
  group_add:
    - video
  environment:
    ROCR_VISIBLE_DEVICES: "0"
```

---

## Dockerfiles

### `backend.Dockerfile`

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

The entrypoint **always runs migrations before starting the server**, ensuring the DB schema is initialized on every `compose up`.

### `frontend.Dockerfile`

Builds the Vite app and serves it on port 3000.

---

## Ports

| Service    | Port | Description                  |
| ---------- | ---- | ---------------------------- |
| Frontend   | 3000 | React app                    |
| Backend    | 8000 | FastAPI (OpenAPI at `/docs`) |
| vLLM       | 8080 | OpenAI-compatible endpoint   |
| PostgreSQL | 5432 | Internal only (not exposed)  |

---

## Volumes

| Volume     | Purpose                    |
| ---------- | -------------------------- |
| `pgdata`   | PostgreSQL data persistence |
| `hf_cache` | HuggingFace model cache    |
