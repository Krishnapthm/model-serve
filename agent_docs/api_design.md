# API Design

## Base URL

```
http://localhost:8000/api/v1
```

OpenAPI docs available at `http://localhost:8000/docs`.

---

## Authentication

Most endpoints require an API key in the `X-API-Key` header.

Public endpoints:

- `GET /health`
- `GET /models`
- `GET /models/{model_id}`

Bootstrap behavior: `POST /keys` is allowed without `X-API-Key` only when there are zero active keys. Once a key exists, `POST /keys` also requires auth.

```http
X-API-Key: sk-ms_AbCdEfGh...
```

The full key is shown **once** on creation. Only the prefix and bcrypt hash are stored.

---

## Endpoint Overview

### Models

| Method | Path                 | Description                                                   |
| ------ | -------------------- | ------------------------------------------------------------- |
| `GET`  | `/models`            | List HF models, supports `?category=` filter and `?q=` search |
| `GET`  | `/models/{model_id}` | Model detail + link to HF model card                          |

### Serve

| Method   | Path          | Description                     |
| -------- | ------------- | ------------------------------- |
| `POST`   | `/serve`      | Pull and serve a model via vLLM |
| `GET`    | `/serve`      | List currently served models    |
| `DELETE` | `/serve/{id}` | Stop a served model             |

### API Keys

| Method   | Path         | Description                            |
| -------- | ------------ | -------------------------------------- |
| `POST`   | `/keys`      | Create a new API key                   |
| `GET`    | `/keys`      | List all keys (prefix + metadata only) |
| `DELETE` | `/keys/{id}` | Revoke a key                           |

### Health

| Method | Path      | Description              |
| ------ | --------- | ------------------------ |
| `GET`  | `/health` | Service health (no auth) |

---

## Response Shape

### Success

```json
{
  "data": { ... },
  "meta": { "page": 1, "total": 42 }
}
```

### Error

```json
{
  "detail": "Human-readable error message",
  "code": "MODEL_NOT_FOUND"
}
```

Error codes are defined in `app/utils/error_codes.py`.

---

## POST /serve Request & Response

```json
// Request
{
  "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
  "gpu_type": "cuda"
}

// Response 202 Accepted
{
  "data": {
    "id": "uuid",
    "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
    "status": "pending",
    "endpoint_url": "http://localhost:8080/v1",
    "env_snippet": {
      "OPENAI_API_KEY": "sk-ms_AbCdEfGh",
      "OPENAI_BASE_URL": "http://localhost:8080/v1"
    }
  }
}
```

Poll `GET /serve/{id}` until `status` becomes `running`.

---

## Pagination

List endpoints accept `?page=1&page_size=20`. Default `page_size` is 20, max is 100.

---

## HuggingFace Hub Caching

The backend caches HF model list responses. Do not call the HF API more than once per 5 minutes for the same query. Cache is stored in-process (or Redis if scaled). See `app/services/huggingface.py` for TTL config.
