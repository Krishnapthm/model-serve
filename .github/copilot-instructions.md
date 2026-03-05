# ModelServe — Global Instructions

A self-hosted GPU model serving platform.
**Stack:** FastAPI · PostgreSQL · React (Vite) · shadcn/ui · vLLM · Docker Compose (CUDA + ROCm)

## Project Layout

```
/
├── backend/          # FastAPI app (uv) — see backend/README.md
├── frontend/         # Vite + React + shadcn/ui — see frontend/README.md
├── docker/           # Compose files, Dockerfiles — see docker/README.md
├── docs/             # Cross-cutting docs (architecture, deployment, API)
└── README.md         # User-facing quickstart
```

## Core Rules

- **DRY + SOLID.** No logic duplication. One responsibility per module/component.
- **Dependency injection everywhere** in FastAPI. Never import services directly into routers.
- **uv only** for Python dependency management. Never pip, never poetry.
- **shadcn/ui only** for all UI components. Never install raw Radix, Headless UI, or MUI.
- **No native scrollbars.** Use shadcn `ScrollArea` everywhere.
- **TanStack Query** for all server state. Never call APIs directly in components or `useEffect`.
- **Keep documentation current.** After changes, update the relevant directory README.md and `docs/` files when the change affects cross-cutting concerns.

## Verification

```bash
# Backend
cd backend && uv run pytest

# Frontend
cd frontend && npm run typecheck && npm run lint

# Full stack
docker compose -f docker/compose.cuda.yml up --build
```

If tests or types fail, fix them before considering a task done.
