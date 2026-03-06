# Docker

Docker Compose setup for ModelServe. Provides AMD ROCm GPU-accelerated and local development configurations.

---

## Compose Files

| File                | Purpose                                         |
| ------------------- | ----------------------------------------------- |
| `compose.base.yml`  | Shared service config — extended by other files |
| `compose.rocm.yml`  | AMD GPU stack (`/dev/kfd` + `/dev/dri`)         |
| `compose.local.yml` | Local dev — DB + backend + frontend HMR, no GPU |

---

## Quickstart

```bash
# From repo root:

# AMD ROCm
docker compose -f docker/compose.rocm.yml up --build

# Local development (no GPU)
docker compose -f docker/compose.local.yml up --build
```

---

## Service Topology

```yaml
services:
  db: # PostgreSQL 17 — healthcheck enabled
  backend: # FastAPI — depends on db, runs migrations on start
  frontend: # Vite/React — serves on :3000
  # vLLM containers are spawned dynamically by the backend via the Docker SDK.
```

### ROCm-specific Config

vLLM containers spawned at runtime use the official prebuilt image with these
flags (mirroring the [vLLM ROCm docs](https://docs.vllm.ai/en/stable/deployment/docker/#amd-rocm)):

```yaml
image: vllm/vllm-openai-rocm:latest
ipc_mode: host
devices:
  - /dev/kfd
  - /dev/dri/renderD128   # enumerated at runtime via glob — not passed as a dir
  - /dev/dri/card0
group_add:
  - video   # GID for /dev/dri/card0
  - render  # GID for /dev/kfd and /dev/dri/renderD128
cap_add:
  - SYS_PTRACE
security_opt:
  - seccomp=unconfined
```

> **Note:** The Docker Python SDK requires individual device *file* paths — passing
> `/dev/dri` (a directory) silently skips the render nodes. `vllm_manager.py` uses
> `glob.glob` to enumerate the actual files at container-spawn time.

> **Known issue:** Containers are currently exiting immediately on this host.
> See [docs/rocm-container-troubleshooting.md](../docs/rocm-container-troubleshooting.md).

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

| Volume     | Purpose                     |
| ---------- | --------------------------- |
| `pgdata`   | PostgreSQL data persistence |
| `hf_cache` | HuggingFace model cache     |
