# Deployment

## Prerequisites

| Requirement | Minimum |
| ----------- | ------- |
| Docker Engine | 24+ |
| Docker Compose | v2.20+ (profiles support) |
| AMD GPU | gfx900+ (Vega, RDNA, CDNA) |
| ROCm driver | 6.x |
| Host RAM | 16 GB (model-dependent) |
| VRAM | Depends on model size |

---

## Quick Start

```bash
git clone https://github.com/<org>/model-serve.git
cd model-serve

# Copy and edit environment
cp .env.example .env
# At minimum set: VLLM_MODEL_1, SECRET_KEY, POSTGRES_PASSWORD
```

Edit `.env`:

```dotenv
# Required
SECRET_KEY=change-me-to-random-string
POSTGRES_PASSWORD=change-me
VLLM_MODEL_1=meta-llama/Llama-3.1-8B-Instruct

# Optional — serve up to 4 models
VLLM_MODEL_2=mistralai/Mistral-7B-Instruct-v0.3

# Optional — protect vLLM endpoints
VLLM_API_KEY=your-key-here

# HuggingFace token — required for gated models
HF_TOKEN=hf_xxxxx
```

Start the stack:

```bash
# Serve model 1 only
docker compose -f docker/compose.base.yml \
               -f docker/compose.rocm.yml \
               --profile vllm-1 up -d

# Serve models 1 and 2
docker compose -f docker/compose.base.yml \
               -f docker/compose.rocm.yml \
               --profile vllm-1 --profile vllm-2 up -d
```

---

## First Run vs Subsequent Runs

### First run

vLLM downloads the model from HuggingFace Hub. This can take minutes to hours depending on model size and bandwidth.

```text
vllm-1  | Downloading model 'meta-llama/Llama-3.1-8B-Instruct'...
vllm-1  | [========>                     ] 32%  ETA 5:23
```

The downloaded weights are cached in the Docker volume `hf-cache`.

### Subsequent runs

vLLM finds the cached weights and starts serving in seconds:

```text
vllm-1  | Loading cached model from /root/.cache/huggingface/...
vllm-1  | INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Do not delete the `hf-cache` volume** unless you want to re-download all models.

```bash
# View cache volume
docker volume inspect model-serve_hf-cache

# Force re-download (destructive)
docker compose down -v   # removes ALL volumes including database
```

---

## Environment Reference

### Core

| Variable | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `SECRET_KEY` | yes | — | JWT signing key |
| `POSTGRES_PASSWORD` | yes | — | Database password |
| `DATABASE_URL` | no | built from PG vars | Full async connection string |

### Model Slots

| Variable | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `VLLM_MODEL_1` | yes | — | HuggingFace model ID for slot 1 |
| `VLLM_MODEL_2` | no | — | HuggingFace model ID for slot 2 |
| `VLLM_MODEL_3` | no | — | HuggingFace model ID for slot 3 |
| `VLLM_MODEL_4` | no | — | HuggingFace model ID for slot 4 |

### vLLM

| Variable | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `VLLM_HOST` | no | `localhost` | Hostname for vLLM services |
| `VLLM_BASE_PORT` | no | `8081` | Port of slot 1 (slots increment by 1) |
| `VLLM_API_KEY` | no | — | Bearer token for vLLM endpoints |
| `VLLM_ROCM_IMAGE` | no | `vllm/vllm-openai-rocm:latest` | vLLM Docker image |
| `HF_TOKEN` | no | — | HuggingFace token for gated models |
| `VLLM_PORT_1`–`VLLM_PORT_4` | no | 8081–8084 | Override individual slot ports |

### Application

| Variable | Required | Default | Description |
| -------- | -------- | ------- | ----------- |
| `APP_NAME` | no | `ModelServe` | Display name |
| `API_V1_PREFIX` | no | `/api/v1` | API route prefix |
| `BACKEND_CORS_ORIGINS` | no | `["*"]` | Allowed CORS origins |

---

## Profiles

Each vLLM slot is behind a Docker Compose profile. Only activated slots consume GPU resources.

| Profile | Service | Port | Env Var |
| ------- | ------- | ---- | ------- |
| `vllm-1` | vllm-1 | 8081 | `VLLM_MODEL_1` |
| `vllm-2` | vllm-2 | 8082 | `VLLM_MODEL_2` |
| `vllm-3` | vllm-3 | 8083 | `VLLM_MODEL_3` |
| `vllm-4` | vllm-4 | 8084 | `VLLM_MODEL_4` |

---

## Production Considerations

### GPU Isolation

Each vLLM service gets `/dev/kfd` and `/dev/dri`. For multi-GPU systems, use `HIP_VISIBLE_DEVICES` to pin services to specific GPUs:

```yaml
# In a custom override file
services:
  vllm-1:
    environment:
      HIP_VISIBLE_DEVICES: "0"
  vllm-2:
    environment:
      HIP_VISIBLE_DEVICES: "1"
```

### Monitoring

Monitor vLLM directly:

```bash
# Health
curl http://localhost:8081/health

# Metrics (Prometheus format)
curl http://localhost:8081/metrics
```

### Reverse Proxy

Place a reverse proxy in front for TLS termination:

```text
Client → nginx (443) → backend (8000)
                      → vllm-1 (8081)
                      → vllm-2 (8082)
```

### Backup

Back up the PostgreSQL volume regularly. The `hf-cache` volume is a cache and can be regenerated (but re-download takes time).

```bash
docker compose exec postgres pg_dump -U modelserve modelserve > backup.sql
```

---

## Troubleshooting

| Symptom | Cause | Fix |
| ------- | ----- | --- |
| `Permission denied: /dev/kfd` | ROCm not installed or user not in `render`/`video` groups | `sudo usermod -aG render,video $USER` and re-login |
| vLLM OOM during model load | Not enough VRAM | Use a smaller model or enable quantization via vLLM args |
| Model download hangs | Gated model without token | Set `HF_TOKEN` in `.env` |
| Backend shows all models as `loading` | vLLM still downloading or crashed | Check `docker compose logs vllm-1` |
| Port conflict on 8081 | Another service on that port | Change `VLLM_PORT_1` in `.env` |
