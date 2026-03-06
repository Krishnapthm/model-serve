# API Reference

Base URL: `http://localhost:8000/api/v1`

All endpoints return JSON. Errors follow a consistent shape:

```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable message"
  }
}
```

---

## Authentication

### POST /auth/signup

Create a new user.

**Request:**

```json
{
  "username": "alice",
  "password": "hunter2"
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "username": "alice"
}
```

### POST /auth/login

Obtain a JWT access token.

**Request:**

```json
{
  "username": "alice",
  "password": "hunter2"
}
```

**Response (200):**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## Models (Public)

### GET /models

List all configured model slots with health status.

**Auth:** None required.

**Response (200):**

```json
[
  {
    "slot": 1,
    "model_id": "meta-llama/Llama-3.1-8B-Instruct",
    "display_name": "Llama-3.1-8B-Instruct",
    "endpoint_url": "http://localhost:8081/v1",
    "status": "running",
    "env_snippet": "export OPENAI_BASE_URL=http://localhost:8081/v1"
  }
]
```

| Field | Type | Description |
| ----- | ---- | ----------- |
| `slot` | int | Slot number (1–4) |
| `model_id` | string | HuggingFace model ID |
| `display_name` | string | Short name (last segment of model_id) |
| `endpoint_url` | string | OpenAI-compatible base URL |
| `status` | string | `running` or `loading` |
| `env_snippet` | string | Shell export line for OpenAI SDK |

### GET /models/{slot}

Get a single model slot.

**Auth:** None required.

**Response (200):** Same shape as one item in the list.

**Response (404):**

```json
{
  "detail": "Slot not configured"
}
```

---

## Serve (Authenticated)

### GET /serve

List all configured model slots (same data as `/models` but requires auth).

**Auth:** `Authorization: Bearer <token>`

**Response (200):** Same shape as `GET /models`.

### GET /serve/{slot}

Get a single model slot (authenticated).

**Auth:** `Authorization: Bearer <token>`

**Response (200):** Same shape as one item in the list.

**Response (404):**

```json
{
  "detail": "Slot not configured"
}
```

> **Removed in v0.2.0:** `POST /serve` (deploy model) and `DELETE /serve/{id}` (stop model) no longer exist. Models are configured at deploy time via environment variables.

---

## API Keys

### GET /keys

List all API keys for the authenticated user.

**Auth:** `Authorization: Bearer <token>`

**Response (200):**

```json
[
  {
    "id": "uuid",
    "name": "my-key",
    "prefix": "ms-abc",
    "created_at": "2025-01-01T00:00:00Z",
    "last_used_at": null,
    "is_active": true
  }
]
```

### POST /keys

Create a new API key. The full key is returned only once.

**Auth:** `Authorization: Bearer <token>`

**Request:**

```json
{
  "name": "my-key"
}
```

**Response (201):**

```json
{
  "id": "uuid",
  "name": "my-key",
  "prefix": "ms-abc",
  "key": "ms-abcdef1234567890",
  "created_at": "2025-01-01T00:00:00Z",
  "is_active": true
}
```

### DELETE /keys/{key_id}

Revoke an API key.

**Auth:** `Authorization: Bearer <token>`

**Response (204):** No content.

---

## Health

### GET /health

**Auth:** None required.

**Response (200):**

```json
{
  "status": "healthy"
}
```

---

## Error Codes

| Code | HTTP Status | Description |
| ---- | ----------- | ----------- |
| `KEY_NOT_FOUND` | 404 | API key does not exist |
| `INVALID_API_KEY` | 401 | API key is invalid or revoked |
| `USER_ALREADY_EXISTS` | 409 | Username is taken |
| `INVALID_CREDENTIALS` | 401 | Wrong username or password |
| `INVALID_AUTH_TOKEN` | 401 | JWT is expired or malformed |

> **Removed in v0.2.0:** `MODEL_NOT_FOUND`, `MODEL_PULL_ERROR`, `GPU_UNAVAILABLE`, `SERVED_MODEL_NOT_FOUND`, `VLLM_ERROR` — these no longer apply since model lifecycle is managed by Docker Compose, not the backend.
