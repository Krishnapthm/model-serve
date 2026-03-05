# Frontend Conventions

## Component Library — shadcn/ui (mandatory)

**Only use shadcn/ui components.** Never install raw Radix UI, Headless UI, MUI, Chakra, or Mantine.

```bash
# Add a new shadcn component
npx shadcn@latest add dialog
npx shadcn@latest add sonner
```

Components land in `src/components/ui/` — **do not hand-edit these files.**
App-specific compositions go in `src/components/app/`.

---

## Component Reuse Rule

Before creating a new component:

1. Check `src/components/ui/` (shadcn primitives)
2. Check `src/components/app/` (existing app components)
3. Only create a new file in `src/components/app/` if neither works.

---

## Scrollbars

**Zero native scrollbars allowed anywhere in the app.**
Wrap every scrollable region with shadcn `ScrollArea`.

```tsx
import { ScrollArea } from "@/components/ui/scroll-area"

<ScrollArea className="h-[600px]">
  {items.map(...)}
</ScrollArea>
```

---

## Toast / Notifications — Sonner

Use `sonner` (shadcn integrated) for all user feedback

---

## Backdrop Blur — Floating Elements

Apply `backdrop-blur-md bg-background/80` to **all floating elements**:

- `Dialog` / `AlertDialog` overlays
- Sticky / floating headers
- Sonner toasts
- Dropdowns/popovers that overlay content

```tsx
<DialogContent className="backdrop-blur-md bg-background/80 border border-border/50">
```

---

## Model Type Badges

Use the shadcn `Badge` component with the correct terminology and variant:

```tsx
import { Badge } from "@/components/ui/badge"

const MODEL_TYPE_BADGE: Record<string, { label: string; variant: BadgeVariant }> = {
  "text-generation":            { label: "LLM",               variant: "default" },
  "feature-extraction":         { label: "Text Embedding",    variant: "secondary" },
  "text-to-image":              { label: "Image Generation",  variant: "outline" },
  "text-to-video":              { label: "Video Generation",  variant: "destructive" },
  "automatic-speech-recognition": { label: "Speech-to-Text", variant: "secondary" },
  "image-to-text":              { label: "Vision-Language",   variant: "outline" },
}

<Badge variant={badge.variant}>{badge.label}</Badge>
```

---

## Data Fetching — TanStack Query (mandatory)

All server state goes through TanStack Query. No raw `fetch`/`axios` in components.
No data-fetching in `useEffect`.

```tsx
// hooks/useModels.ts
export function useModels(category?: string) {
  return useQuery({
    queryKey: ["models", category],
    queryFn: () => api.getModels(category),
    staleTime: 5 * 60 * 1000, // 5 min — HF model list doesn't change often
    gcTime: 30 * 60 * 1000,
  });
}

// hooks/useServeModel.ts
export function useServeModel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: api.serveModel,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["served-models"] }),
    onError: (err) =>
      toast.error("Failed to serve model", { description: err.message }),
  });
}
```

**Cache rules:**

- HF model list: `staleTime: 5min` — don't hammer the HF API.
- Served model status: `staleTime: 30s`, poll with `refetchInterval: 10000` while status is `pending`.
- API keys: `staleTime: 0` — always fresh after mutations.

## Auth Flow

- Auth pages live at `/login` and `/signup`.
- Use prebuilt shadcn blocks (`login-01`, `signup-01`) as the base UI.
- Persist the bearer token in localStorage and set `Authorization: Bearer <token>` via the shared API client.
- Protect app routes with a route guard component (`ProtectedRoute`) that validates `/auth/me` through TanStack Query.
- Logout must clear local token state and clear TanStack Query cache.

---

## Search

The model search filter must be **client-side** against the cached TanStack Query data.
Never fire a new API request on each keystroke.

```tsx
const { data: models } = useModels();

const filtered = useMemo(
  () =>
    models?.filter(
      (m) =>
        m.id.toLowerCase().includes(query.toLowerCase()) ||
        m.description?.toLowerCase().includes(query.toLowerCase()),
    ),
  [models, query],
);
```

Use a debounced input (250ms) to avoid unnecessary re-renders.

---

## State Management Summary

| State type                          | Where it lives            |
| ----------------------------------- | ------------------------- |
| Server data (models, keys, served)  | TanStack Query            |
| UI state (modals, selected model)   | `useState` / `useReducer` |
| Global UI (theme, HF token)         | React Context or Zustand  |
| URL state (category filter, search) | URL search params         |

---

## TypeScript

- Strict mode enabled. No `any`.
- API response types generated from backend OpenAPI spec (or manually mirrored in `src/types/`).
- Always define prop types inline with `interface`, not `type =`.

```bash
npm run typecheck   # tsc --noEmit
npm run lint        # eslint + biome
```
