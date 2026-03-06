# Frontend Migration Reference — v0.2.0

> **Purpose:** This document describes every backend change made in the
> `refactor/rocm-compose-only` branch so the frontend agent can rebuild
> affected pages, hooks, types, and API calls.

---

## 1. High-Level Summary

| What changed | Detail |
| ------------ | ------ |
| Model discovery removed | No more HuggingFace Hub browsing. Models are declared at deploy time via env vars. |
| Model lifecycle removed | `POST /serve` (deploy) and `DELETE /serve/{id}` (stop) no longer exist. |
| Slot-based model listing | Models are identified by **slot number** (1–4), not UUID. |
| Status simplified | Only two statuses: `running` and `loading`. `pending`, `stopped`, `error` are gone. |
| No pagination on models | `/models` returns a flat list (max 4 items). No `PaginatedResponse`. |
| `env_snippet` is a string | Was `{ OPENAI_API_KEY, OPENAI_BASE_URL }` object, now a shell `export` string. |
| Auth unchanged | JWT login/signup, API key CRUD — all identical. |

---

## 2. Removed Endpoints

These endpoints no longer exist. Any frontend code calling them must be removed.

| Old Endpoint | Purpose | Replacement |
| ------------ | ------- | ----------- |
| `GET /models?category=&q=&page=&page_size=` | Browse HuggingFace Hub | `GET /models` (no params, returns configured slots) |
| `GET /models/{model_id}` (string HF model ID) | HuggingFace model detail | `GET /models/{slot}` (integer slot number) |
| `POST /serve` | Deploy a model | Removed — models are configured at deploy time |
| `DELETE /serve/{id}` | Stop a model | Removed — models are managed by Docker Compose |

---

## 3. Changed Endpoints

### `GET /models`

**Before (v0.1.0):**
```json
{
  "data": [
    {
      "id": "meta-llama/Llama-3.1-8B-Instruct",
      "name": "Llama-3.1-8B-Instruct",
      "pipeline_tag": "text-generation",
      "description": "...",
      "downloads": 1234567,
      "likes": 5432,
      "label": "LLM",
      "badge_color": "blue"
    }
  ],
  "meta": { "page": 1, "page_size": 20, "total": 100 }
}
```

**After (v0.2.0):**
```json
{
  "data": [
    {
      "slot": 1,
      "model_id": "meta-llama/Llama-3.1-8B-Instruct",
      "display_name": "Llama-3.1-8B-Instruct",
      "endpoint_url": "http://localhost:8081/v1",
      "status": "running",
      "env_snippet": "export OPENAI_BASE_URL=http://localhost:8081/v1"
    }
  ]
}
```

- **No query parameters** — no category, search, page, page_size.
- **No `meta`** — no pagination.
- **Auth:** Not required (public endpoint).

### `GET /models/{slot}`

**Path parameter** is now an **integer** (1–4), not a HuggingFace model ID string.

**Response:** Same shape as one item in the list above, wrapped in `{ "data": ... }`.

**404** when slot is not configured:
```json
{ "detail": "Model slot 1 is not configured" }
```

### `GET /serve`

**Before:** Returned `ServedModel[]` with fields: `id` (UUID), `model_id`, `display_name`, `pipeline_tag`, `status` (pending|running|stopped|error), `endpoint_url`, `gpu_type`, `started_at`, `stopped_at`, `env_snippet` (object).

**After:** Returns the same data as `GET /models` (slot-based), just behind auth.
```json
{
  "data": [
    {
      "slot": 1,
      "model_id": "meta-llama/Llama-3.1-8B-Instruct",
      "display_name": "Llama-3.1-8B-Instruct",
      "endpoint_url": "http://localhost:8081/v1",
      "status": "running",
      "env_snippet": "export OPENAI_BASE_URL=http://localhost:8081/v1"
    }
  ]
}
```

### `GET /serve/{slot}`

Same as `GET /models/{slot}` but requires auth. Path param is integer slot number.

---

## 4. Type Changes Required

### Delete: `types/models.ts`

The entire file is obsolete. There is no `ModelSummary`, `ModelDetail`, `ModelCategory`, or `CATEGORY_LABELS` anymore.

### Rewrite: `types/serve.ts`

**Old type:**
```typescript
export type ModelStatus = "pending" | "running" | "stopped" | "error";

export interface ServedModel {
    id: string;
    model_id: string;
    display_name: string;
    pipeline_tag: string | null;
    status: ModelStatus;
    endpoint_url: string | null;
    gpu_type: string;
    started_at: string;
    stopped_at: string | null;
    env_snippet?: {
        OPENAI_API_KEY: string;
        OPENAI_BASE_URL: string;
    };
}

export interface ServeRequest {
    model_id: string;
    gpu_type?: string;
}
```

**New type:**
```typescript
export type ModelStatus = "running" | "loading";

export interface ServedModel {
    slot: number;
    model_id: string;
    display_name: string;
    endpoint_url: string;
    status: ModelStatus;
    env_snippet: string;
}
```

Key differences:
- `id` (UUID) → `slot` (number, 1–4)
- `pipeline_tag` — removed
- `gpu_type` — removed
- `started_at` / `stopped_at` — removed
- `endpoint_url` — always a string, never null
- `env_snippet` — now a `string` (shell export), not an object
- `status` — only `"running"` or `"loading"`
- `ServeRequest` — deleted entirely (no more POST)

### Simplify: `types/api.ts`

`PaginatedResponse<T>` is no longer used by any endpoint. Can be removed or kept for future use.

### No changes: `types/auth.ts`, `types/keys.ts`

These are unchanged.

---

## 5. Hook Changes Required

### Delete: `hooks/useModels.ts`

The HuggingFace browsing hooks (`useModels`, `useModel`) are obsolete. Replace with a simple hook that calls `GET /models`:

```typescript
export function useConfiguredModels() {
    return useQuery({
        queryKey: ["models"],
        queryFn: async () => {
            const { data } = await api.get<{ data: ServedModel[] }>("/models");
            return data.data;
        },
        refetchInterval: 15_000, // Poll for health status
    });
}
```

### Rewrite: `hooks/useServe.ts`

- Remove `useServeModel()` — no `POST /serve`
- Remove `useStopModel()` — no `DELETE /serve/{id}`
- Keep `useServedModels()` but update the response type and polling logic:
  - Poll while any model has `status === "loading"` instead of `"pending"`
  - No mutation hooks needed

### No changes: `hooks/useAuth.ts`, `hooks/useKeys.ts`

These are unchanged.

---

## 6. API Client Changes Required (`lib/api.ts`)

### Remove these functions:
- `getModels(category, q, page, pageSize)` — HF browsing
- `getModel(modelId: string)` — HF detail
- `serveModel(req: ServeRequest)` — deploy
- `stopModel(id: string)` — stop

### Replace with:
```typescript
/** Get all configured model slots with health status. */
export async function getConfiguredModels(): Promise<ServedModel[]> {
    const { data } = await api.get<{ data: ServedModel[] }>("/models");
    return data.data;
}

/** Get a single model slot. */
export async function getConfiguredModel(slot: number): Promise<ServedModel> {
    const { data } = await api.get<{ data: ServedModel }>(`/models/${slot}`);
    return data.data;
}
```

### Update `getServedModels` / `getServedModel`:
```typescript
/** Get served models (authenticated). */
export async function getServedModels(): Promise<ServedModel[]> {
    const { data } = await api.get<{ data: ServedModel[] }>("/serve");
    return data.data;
}

export async function getServedModel(slot: number): Promise<ServedModel> {
    const { data } = await api.get<{ data: ServedModel }>(`/serve/${slot}`);
    return data.data;
}
```

### No changes to: `signup`, `login`, `getMe`, `createKey`, `getKeys`, `revokeKey`, `healthCheck`, `setAuthToken`, `getAuthToken`

---

## 7. Page Changes Required

### `pages/models.tsx` — Complete Rewrite

**Old behavior:** Browse HuggingFace Hub with categories, search, pagination, "Serve" button.

**New behavior:** Show the configured model slots (max 4 cards). Each card shows:
- `display_name` and `model_id`
- `status` badge (running / loading)
- `endpoint_url`
- Copy-to-clipboard button for `env_snippet`

No search, no categories, no pagination, no "Serve" button.

### `pages/served.tsx` — Major Rewrite

**Old behavior:** List served models with Stop button, status polling, click-to-open script dialog.

**New behavior:** Same listing but:
- Remove the Stop button entirely (cannot stop via API)
- Remove `AlertDialog` for stop confirmation
- Key is `slot` not `id`
- Status badge only needs `running` and `loading` states
- Remove `gpu_type`, `started_at`, `stopped_at` display
- The script dialog still works but needs updated types

### `pages/keys.tsx`, `pages/login.tsx`, `pages/signup.tsx` — No Changes

---

## 8. Component Changes Required

### `components/app/model-card.tsx` — Complete Rewrite

**Old:** Shows HF model with badge_color, pipeline_tag label, downloads/likes stats, "Serve" button.

**New:** Shows a configured vLLM slot with:
- `display_name` / `model_id`
- Status badge
- `endpoint_url` (copyable)
- `env_snippet` (copyable)

No "Serve" button, no download/like counts, no category badge.

### `components/app/status-badge.tsx` — Simplify

Remove `pending`, `stopped`, `error` states. Only two states:
- `running` — green badge
- `loading` — yellow/pulsing badge

### `components/app/serve-script-dialog.tsx` — Update

- The `resolveDynamicBaseUrl` function should just use `model.endpoint_url` directly since it's always populated
- `model.env_snippet` is now a string, not `{ OPENAI_API_KEY, OPENAI_BASE_URL }`
- `model.model_id` still works for the script template

### `components/app/env-snippet.tsx` — Update

The props should change since `env_snippet` is now a single shell string:
```typescript
// Old
interface EnvSnippetProps {
    apiKey: string;
    baseUrl: string;
}

// New — just display the preformatted string
interface EnvSnippetProps {
    snippet: string;
}
```

### `components/app/layout.tsx`, `components/app/protected-route.tsx` — No Changes

---

## 9. Navigation / Routing Notes

The old app had a "Models" page for browsing HF models and a "Served" page for running instances. In the new architecture, these concepts merge:

- **Models page** → shows configured slots (from `GET /models`, no auth)
- **Served page** → shows the same slots but behind auth, with more admin-oriented UI

Consider whether you want to keep both pages or merge them into one. The backend serves nearly identical data on both endpoints; the only difference is authentication.

---

## 10. Files to Delete

| File | Reason |
| ---- | ------ |
| `types/models.ts` | HuggingFace model types — no longer used |
| `hooks/useModels.ts` | HuggingFace browsing hooks — no longer used |

---

## 11. Backend Response Schema Reference

```typescript
// The single model type used everywhere now
interface ServedModel {
    slot: number;           // 1-4
    model_id: string;       // e.g. "meta-llama/Llama-3.1-8B-Instruct"
    display_name: string;   // e.g. "Llama-3.1-8B-Instruct"
    endpoint_url: string;   // e.g. "http://localhost:8081/v1"
    status: "running" | "loading";
    env_snippet: string;    // e.g. "export OPENAI_BASE_URL=http://localhost:8081/v1"
}

// All list endpoints return:  { data: ServedModel[] }
// All detail endpoints return: { data: ServedModel }
// Error: { detail: "message string" }
```

If `VLLM_API_KEY` is set, `env_snippet` includes both lines:
```
export OPENAI_BASE_URL=http://localhost:8081/v1
export OPENAI_API_KEY=your-key
```
