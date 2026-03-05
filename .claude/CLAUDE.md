# CLAUDE.md

## Project: ModelServe

A self-hosted GPU model serving platform. Users browse HuggingFace models, click **Serve**, and get an OpenAI-compatible endpoint — no infra knowledge required.

**Stack:** FastAPI · PostgreSQL · React (Vite) · shadcn/ui · vLLM · Docker Compose (CUDA + ROCm)

---

## Before You Start

Read the relevant `agent_docs/` file(s) before making any changes:

| File | When to read |
|---|---|
| `agent_docs/architecture.md` | Project structure, service boundaries, data flow |
| `agent_docs/backend.md` | FastAPI conventions, DI patterns, uv, docstrings |
| `agent_docs/frontend.md` | React rules, shadcn/ui, TanStack Query, state |
| `agent_docs/docker.md` | Compose setup, CUDA vs ROCm, env vars |
| `agent_docs/database.md` | Schema, migrations, initialization on compose up |
| `agent_docs/api_design.md` | Endpoint conventions, API key auth, error shapes |

---

## Core Rules (Always Apply)

- **Docs first.** After every change, update the relevant `agent_docs/` file and the root `README.md`. No exceptions.
- **DRY + SOLID.** No logic duplication. One responsibility per module/component.
- **Dependency injection everywhere** in FastAPI. Never import services directly into routers.
- **uv only** for Python dependency management. Never pip, never poetry.
- **shadcn/ui only** for all UI components. Never install raw Radix, Headless UI, or MUI.
- **No native scrollbars.** Use shadcn `ScrollArea` everywhere.
- **TanStack Query** for all server state. Never call APIs directly in components or `useEffect`.

---

## Quick Orientation

```
/
├── backend/          # FastAPI app (uv)
├── frontend/         # Vite + React + shadcn/ui
├── docker/           # Compose files, Dockerfiles
├── agent_docs/       # Agent reference docs (read before working)
└── README.md         # User-facing quickstart
```

---

## How to Verify Your Work

```bash
# Backend
cd backend && uv run pytest

# Frontend
cd frontend && npm run typecheck && npm run lint

# Full stack
docker compose -f docker/compose.cuda.yml up --build
```

If tests or types fail, fix them before considering a task done.
