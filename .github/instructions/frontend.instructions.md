---
name: 'Frontend Conventions'
description: 'React rules: shadcn/ui only, TanStack Query, ScrollArea, backdrop blur, state management, TypeScript strict'
applyTo: 'frontend/**'
---

# Frontend Coding Conventions

## shadcn/ui Only

**Only use shadcn/ui components.** Never install raw Radix UI, Headless UI, MUI, Chakra, or Mantine.

```bash
npx shadcn@latest add dialog
```

- Generated components live in `src/components/ui/` — **do not hand-edit**.
- App-specific compositions go in `src/components/app/`.

### Component Reuse Order

Before creating a new component:
1. Check `src/components/ui/` (shadcn primitives)
2. Check `src/components/app/` (existing app components)
3. Only create a new file in `src/components/app/` if neither works.

## No Native Scrollbars

Wrap **every** scrollable region with shadcn `ScrollArea`:

```tsx
import { ScrollArea } from "@/components/ui/scroll-area"

<ScrollArea className="h-[600px]">
  {items.map(...)}
</ScrollArea>
```

## Toasts — Sonner

Use `sonner` (shadcn integrated) for all user feedback notifications.

## Backdrop Blur on Floating Elements

Apply `backdrop-blur-md bg-background/80` to **all** floating elements:
- `Dialog` / `AlertDialog` overlays
- Sticky / floating headers
- Sonner toasts
- Dropdowns / popovers that overlay content

```tsx
<DialogContent className="backdrop-blur-md bg-background/80 border border-border/50">
```

## Model Type Badges

Use the shadcn `Badge` component with the correct mapping:

```tsx
const MODEL_TYPE_BADGE: Record<string, { label: string; variant: BadgeVariant }> = {
  "text-generation":              { label: "LLM",              variant: "default" },
  "feature-extraction":           { label: "Text Embedding",   variant: "secondary" },
  "text-to-image":                { label: "Image Generation", variant: "outline" },
  "text-to-video":                { label: "Video Generation", variant: "destructive" },
  "automatic-speech-recognition": { label: "Speech-to-Text",   variant: "secondary" },
  "image-to-text":                { label: "Vision-Language",  variant: "outline" },
}
```

## Data Fetching — TanStack Query

All server state goes through TanStack Query. **No** raw `fetch`/`axios` in components. **No** data-fetching in `useEffect`.

```tsx
// hooks/useModels.ts
export function useModels(category?: string) {
  return useQuery({
    queryKey: ["models", category],
    queryFn: () => api.getModels(category),
    staleTime: 5 * 60 * 1000,
  });
}
```

### Cache Rules

| Data              | staleTime | Notes                                              |
| ----------------- | --------- | -------------------------------------------------- |
| HF model list     | 5 min     | Don't hammer the HF API                            |
| Served model status | 30 sec  | Poll with `refetchInterval: 10000` while `pending` |
| API keys          | 0         | Always fresh after mutations                       |

### Mutations

```tsx
export function useServeModel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.serveModel,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["served-models"] }),
    onError: (err) => toast.error("Failed to serve model", { description: err.message }),
  });
}
```

## Auth Flow

- Auth pages at `/login` and `/signup`.
- Use prebuilt shadcn blocks (`login-01`, `signup-01`) as the base UI.
- Persist bearer token in localStorage; set `Authorization: Bearer <token>` via the shared API client.
- Protect app routes with `ProtectedRoute` (validates `/auth/me` via TanStack Query).
- Logout must clear local token state **and** TanStack Query cache.

## Client-Side Search

Model search must filter **client-side** against cached TanStack Query data. Never fire a new API request per keystroke.

```tsx
const filtered = useMemo(
  () => models?.filter(m =>
    m.id.toLowerCase().includes(query.toLowerCase()) ||
    m.description?.toLowerCase().includes(query.toLowerCase())
  ),
  [models, query],
);
```

Use a debounced input (250ms) to avoid unnecessary re-renders.

## State Management

| State type                          | Where it lives            |
| ----------------------------------- | ------------------------- |
| Server data (models, keys, served)  | TanStack Query            |
| UI state (modals, selected model)   | `useState` / `useReducer` |
| Global UI (theme, HF token)         | React Context or Zustand  |
| URL state (category filter, search) | URL search params         |

## TypeScript

- Strict mode enabled. **No `any`.**
- Define prop types inline with `interface`, not `type =`.
- API response types live in `src/types/` (mirrored from backend OpenAPI spec).
