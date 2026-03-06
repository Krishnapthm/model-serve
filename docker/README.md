# Docker

Docker Compose setup for ModelServe. AMD ROCm GPU-accelerated and local development configurations.

---

## Compose Files

| File                | Purpose                                         |
| ------------------- | ----------------------------------------------- |
| `compose.base.yml`  | Shared service config — extended by other files |
| `compose.rocm.yml`  | AMD GPU stack — vLLM model slots via profiles   |
| `compose.local.yml` | Local dev — DB + backend + frontend HMR, no GPU |

---

## Quickstart

```bash
# Always run from the repo root (so Compose can find .env for variable substitution)

# Configure
cp .env.example .env
# Edit .env — set VLLM_MODEL_1, HF_TOKEN, SECRET_KEY, POSTGRES_PASSWORD

# AMD ROCm — serve one model
docker compose --project-directory . -f docker/compose.rocm.yml --profile vllm-1 up --build

# AMD ROCm — serve two models
docker compose --project-directory . -f docker/compose.rocm.yml --profile vllm-1 --profile vllm-2 up --build

# Local development (no GPU)
docker compose --project-directory . -f docker/compose.local.yml up --build
```

---

## Model Configuration

Models are declared via environment variables in `.env`:

```env
VLLM_MODEL_1=mistralai/Mistral-7B-Instruct-v0.3
VLLM_MODEL_2=meta-llama/Llama-3-8B
VLLM_MODEL_3=
VLLM_MODEL_4=
```

Each slot is activated via a Compose profile:

```bash
# Activate slots 1 and 2 (run from repo root)
docker compose --project-directory . -f docker/compose.rocm.yml --profile vllm-1 --profile vllm-2 up --build
```

Maximum 4 models can be served simultaneously.

### First Run vs Subsequent Runs

- **First run:** vLLM downloads model weights from HuggingFace into the `hf_cache` Docker volume. This takes time depending on model size and network speed.
- **Subsequent runs:** Model weights are loaded from the `hf_cache` volume. Much faster startup.
- **Cache lifetime:** The volume persists across `docker compose down` / `up` cycles. Use `docker volume rm <project>_hf_cache` to force a re-download.

---

## Service Topology

```yaml
services:
  db: # PostgreSQL 17 — healthcheck enabled
  backend: # FastAPI — depends on db, runs migrations on start
  frontend: # Vite/React — serves on :3000
  vllm-1: # vLLM slot 1 (profile: vllm-1) — ROCm
  vllm-2: # vLLM slot 2 (profile: vllm-2) — ROCm
  vllm-3: # vLLM slot 3 (profile: vllm-3) — ROCm
  vllm-4: # vLLM slot 4 (profile: vllm-4) — ROCm
```

### ROCm Configuration

vLLM services use the official prebuilt image with these ROCm flags (per [vLLM AMD docs](https://docs.vllm.ai/en/v0.4.1/getting_started/amd-installation.html)):

```yaml
image: vllm/vllm-openai-rocm:latest
ipc: host
devices:
  - /dev/kfd
  - /dev/dri
group_add:
  - video
cap_add:
  - SYS_PTRACE
security_opt:
  - seccomp=unconfined
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
| vLLM-1     | 8081 | OpenAI-compatible endpoint   |
| vLLM-2     | 8082 | OpenAI-compatible endpoint   |
| vLLM-3     | 8083 | OpenAI-compatible endpoint   |
| vLLM-4     | 8084 | OpenAI-compatible endpoint   |
| PostgreSQL | 5432 | Internal only (not exposed)  |

---

## Volumes

| Volume     | Purpose                                                              |
| ---------- | -------------------------------------------------------------------- |
| `pgdata`   | PostgreSQL data persistence                                          |
| `hf_cache` | HuggingFace model cache — survives restarts, prevents re-downloading |
