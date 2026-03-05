# Deployment

## Prerequisites

- Docker & Docker Compose
- GPU with NVIDIA (CUDA) or AMD (ROCm) drivers
- [HuggingFace token](https://huggingface.co/settings/tokens)

---

## Compose Variants

| File                       | GPU Target    | Runtime                         |
| -------------------------- | ------------- | ------------------------------- |
| `docker/compose.cuda.yml`  | NVIDIA (CUDA) | `nvidia` container runtime      |
| `docker/compose.rocm.yml`  | AMD (ROCm)    | `/dev/kfd` + `/dev/dri` devices |
| `docker/compose.local.yml` | None          | DB + backend + frontend HMR     |

Both GPU files share the same service topology — only the vLLM image tag and GPU device config differ. All shared config is in `docker/compose.base.yml` and extended via `extends`.

---

## Quickstart

```bash
# Clone and enter repo
git clone https://github.com/your-org/modelserve && cd modelserve

# Configure environment
cp .env.example .env
# Edit .env — set HF_TOKEN, SECRET_KEY, POSTGRES_PASSWORD

# NVIDIA GPU
docker compose -f docker/compose.cuda.yml up --build

# AMD GPU
docker compose -f docker/compose.rocm.yml up --build

# Local development (frontend HMR, no GPU/vLLM)
docker compose -f docker/compose.local.yml up --build
```

---

## Environment Variables

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

# CORS (dynamic VPC/public IP friendly defaults)
CORS_ORIGINS=*
CORS_ALLOW_CREDENTIALS=false
CORS_ORIGIN_REGEX=

# vLLM
VLLM_HOST=vllm
VLLM_PORT=8080

# Frontend (optional override; leave empty for dynamic same-host behavior)
VITE_API_BASE_URL=
```

### Environment Variables Reference

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

---

## Ports

| Service    | Port | Description                  |
| ---------- | ---- | ---------------------------- |
| Frontend   | 3000 | React app                    |
| Backend    | 8000 | FastAPI (OpenAPI at `/docs`) |
| vLLM       | 8080 | OpenAI-compatible endpoint   |
| PostgreSQL | 5432 | Internal only (not exposed)  |

---

## Deploying on Changing Public IPs (GPU VPC)

- Frontend API calls auto-resolve to the current browser host on port `8000`, so you do not need to hardcode a fixed public IP.
- Keep `VITE_API_BASE_URL` empty in `.env` unless you intentionally want a custom backend URL.
- Default CORS in `.env.example` is `CORS_ORIGINS=*` (with `CORS_ALLOW_CREDENTIALS=false`) to avoid CORS breaks when the public origin changes.
- For stricter production security, replace `CORS_ORIGINS=*` with a comma-separated allowlist of your exact frontend origins.

---

## Database Initialization

The DB schema is applied automatically on `docker compose up` via Alembic `upgrade head` in the backend container entrypoint. There is no manual migration step for users.

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
