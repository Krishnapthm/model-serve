# API Design

## Base URL

```
http://localhost:8000/api/v1
```

OpenAPI docs available at `http://localhost:8000/docs`.

---

## Authentication

Management endpoints require a bearer token in the `Authorization` header.

Public endpoints:

- `GET /health`
- `GET /models`
- `GET /models/{model_id}`
- `POST /auth/signup`
- `POST /auth/login`

```http
Authorization: Bearer <access_token>
```

API keys created through `POST /keys` are for served-model client usage (`OPENAI_API_KEY`) and are always stored hashed.

---

## Endpoint Overview

### Models

| Method | Path                 | Description                                                   |
| ------ | -------------------- | ------------------------------------------------------------- |
| `GET`  | `/models`            | List HF models, supports `?category=` filter and `?q=` search |
| `GET`  | `/models/{model_id}` | Model detail + link to HF model card                          |

### Auth

| Method | Path           | Description                                |
| ------ | -------------- | ------------------------------------------ |
| `POST` | `/auth/signup` | Create user and return bearer access token |
| `POST` | `/auth/login`  | Login and return bearer access token       |
| `GET`  | `/auth/me`     | Get current authenticated user             |

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

All `Serve` and `API Keys` routes require bearer auth.

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
