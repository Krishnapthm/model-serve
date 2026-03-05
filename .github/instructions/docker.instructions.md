---
name: "Docker Conventions"
description: "Compose structure, base+extends pattern, GPU runtime config, Dockerfile entrypoint conventions"
applyTo: "docker/**"
---

# Docker Conventions

## Compose Structure

- All shared service config lives in `compose.base.yml` and is extended via `extends` in variant files.
- GPU-specific compose files (`compose.cuda.yml`, `compose.rocm.yml`) only override GPU runtime and vLLM image config.
- `compose.local.yml` is for local dev without GPU — no vLLM service.

## Backend Entrypoint

The backend container **always runs migrations before starting the server**:

```dockerfile
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

Never remove the `alembic upgrade head` step. This ensures zero manual migration steps for users.

## GPU Runtime Conventions

### NVIDIA (CUDA)

```yaml
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: all
          capabilities: [gpu]
```

### AMD (ROCm)

```yaml
devices:
  - /dev/kfd
  - /dev/dri
group_add:
  - video
environment:
  ROCR_VISIBLE_DEVICES: "0"
```

## Database Service

Always include a healthcheck on `db` and make `backend` depend on `condition: service_healthy`:

```yaml
db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER"]
```

## Environment

- All services use `env_file: ../.env` pointing to the root `.env`.
- New environment variables must be documented in `.env.example`.
- `VITE_API_BASE_URL` should default to empty (dynamic same-host behavior).

## Volumes

- `pgdata` for PostgreSQL persistence.
- `hf_cache` for HuggingFace model cache (prevents re-downloading).

## Ports

Keep port assignments consistent: frontend `:3000`, backend `:8000`, vLLM `:8080`, PostgreSQL `:5432` (internal only).
