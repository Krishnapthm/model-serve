# API Reference

## Base URL

```
http://localhost:8000/api/v1
```

Interactive OpenAPI docs at `http://localhost:8000/docs`.

---

## Authentication

### Dashboard Auth (Bearer Token)

Management endpoints require a bearer token from signup/login:

```http
Authorization: Bearer <access_token>
```

### Model Client Auth (API Key)

API keys created through `POST /keys` are for served-model client usage (`OPENAI_API_KEY`). Keys are always stored hashed — the plaintext is returned only once at creation time.

### Public Endpoints (No Auth)

- `GET /health`
- `GET /models`
- `GET /models/{model_id}`
- `POST /auth/signup`
- `POST /auth/login`

---

## Endpoints

### Auth

| Method | Path           | Auth | Description                                |
| ------ | -------------- | ---- | ------------------------------------------ |
| `POST` | `/auth/signup` | No   | Create user and return bearer access token |
| `POST` | `/auth/login`  | No   | Login and return bearer access token       |
| `GET`  | `/auth/me`     | Yes  | Get current authenticated user             |

### Models

| Method | Path                 | Auth | Description                                                   |
| ------ | -------------------- | ---- | ------------------------------------------------------------- |
| `GET`  | `/models`            | No   | List HF models, supports `?category=` filter and `?q=` search |
| `GET`  | `/models/{model_id}` | No   | Model detail + link to HF model card                          |

### Serve

| Method   | Path          | Auth | Description                     |
| -------- | ------------- | ---- | ------------------------------- |
| `POST`   | `/serve`      | Yes  | Pull and serve a model via vLLM |
| `GET`    | `/serve`      | Yes  | List currently served models    |
| `DELETE` | `/serve/{id}` | Yes  | Stop a served model             |

### API Keys

| Method   | Path         | Auth | Description                            |
| -------- | ------------ | ---- | -------------------------------------- |
| `POST`   | `/keys`      | Yes  | Create a new API key                   |
| `GET`    | `/keys`      | Yes  | List all keys (prefix + metadata only) |
| `DELETE` | `/keys/{id}` | Yes  | Revoke a key                           |

### Health

| Method | Path      | Auth | Description              |
| ------ | --------- | ---- | ------------------------ |
| `GET`  | `/health` | No   | Service health (no auth) |

---

## Response Shapes

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

Error codes are defined in `backend/app/utils/error_codes.py`.

---

## POST /serve — Example

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

The backend caches HF model list responses. The HF API is not called more than once per 5 minutes for the same query. Cache is stored in-process (or Redis if scaled). See `backend/app/services/huggingface.py` for TTL config.
