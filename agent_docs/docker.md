# Docker Setup

## Two Compose Files

| File | GPU Target | Runtime |
|---|---|---|
| `docker/compose.cuda.yml` | NVIDIA (CUDA) | `nvidia` container runtime |
| `docker/compose.rocm.yml` | AMD (ROCm) | `/dev/kfd` + `/dev/dri` devices |

Both files share the same service topology — only the vLLM image tag and GPU device config differ.
All shared config is in `docker/compose.base.yml` and extended via `extends`.

---

## Quickstart Commands

```bash
# Clone and enter repo
git clone https://github.com/your-org/modelserve && cd modelserve

# Copy env file
cp .env.example .env
# Edit .env — set HF_TOKEN, SECRET_KEY, POSTGRES_PASSWORD

# NVIDIA
docker compose -f docker/compose.cuda.yml up --build

# AMD
docker compose -f docker/compose.rocm.yml up --build
```

---

## compose.cuda.yml Structure

```yaml
services:
  db:
    image: postgres:16-alpine
    env_file: ../.env
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER"]

  backend:
    build:
      context: ../backend
      dockerfile: ../docker/backend.Dockerfile
    env_file: ../.env
    depends_on:
      db:
        condition: service_healthy
    # Runs: alembic upgrade head && uvicorn ...
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  frontend:
    build:
      context: ../frontend
      dockerfile: ../docker/frontend.Dockerfile
    ports: ["3000:3000"]
    environment:
      VITE_API_BASE_URL: http://backend:8000

  vllm:
    image: vllm/vllm-openai:latest
    runtime: nvidia
    env_file: ../.env
    volumes:
      - hf_cache:/root/.cache/huggingface
    # Model + port passed at serve time via backend exec
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

volumes:
  pgdata:
  hf_cache:
```

---

## compose.rocm.yml Differences

```yaml
services:
  vllm:
    image: vllm/vllm-openai:rocm   # ROCm-specific image
    # No runtime: nvidia
    devices:
      - /dev/kfd
      - /dev/dri
    group_add:
      - video
    environment:
      ROCR_VISIBLE_DEVICES: "0"    # Adjust per your AMD GPU count
```

---

## Backend Dockerfile Entrypoint

The backend container **always runs migrations before starting the server**. This ensures the DB schema is initialized on every `compose up` without manual steps.

```dockerfile
# docker/backend.Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

---

## Environment Variables Reference

Create `.env` from `.env.example`. Required vars:

```bash
# HuggingFace
HF_TOKEN=hf_...

# Database
POSTGRES_USER=modelserve
POSTGRES_PASSWORD=changeme
POSTGRES_DB=modelserve
DATABASE_URL=postgresql+asyncpg://modelserve:changeme@db:5432/modelserve

# Security
SECRET_KEY=your-random-secret-key-min-32-chars

# vLLM
VLLM_HOST=vllm
VLLM_PORT=8080
```

---

## Custom vLLM Build

If you have a custom vLLM image (e.g. with custom kernels or quantization support):

1. Build your image: `docker build -t my-vllm:latest ./custom-vllm`
2. In your compose file, replace the `image:` field:
   ```yaml
   vllm:
     image: my-vllm:latest
   ```
3. All other config (devices, volumes, env) stays the same.
4. Document any extra env vars your image requires in `.env.example`.

The backend's `vllm_manager.py` service spawns vLLM via the Docker socket using the configured image name — no other changes needed.

---

## Ports

| Service | Port | Description |
|---|---|---|
| Frontend | 3000 | React app |
| Backend | 8000 | FastAPI (OpenAPI at `/docs`) |
| vLLM | 8080 | OpenAI-compatible endpoint |
| PostgreSQL | 5432 | Internal only (not exposed) |
