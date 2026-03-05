---
name: 'Documentation Standards'
description: 'Rules for writing and maintaining project documentation — README.md placement, docs/ folder structure, and content guidelines'
applyTo: '**/*.md'
---

# Documentation Standards

## Documentation Architecture

This project separates **documentation** (for humans) from **agent instructions** (for AI coding agents):

| Content                          | Location                                | Format              |
| -------------------------------- | --------------------------------------- | ------------------- |
| Directory-specific docs          | `<dir>/README.md`                       | Markdown            |
| Cross-cutting docs               | `docs/<topic>.md`                       | Markdown            |
| Always-on agent rules            | `.github/copilot-instructions.md`       | Markdown            |
| File-scoped agent rules          | `.github/instructions/*.instructions.md`| Markdown + YAML front matter |
| Claude-compatible agent rules    | `.claude/CLAUDE.md`                     | Markdown            |

### Where to Put Documentation

**Per-directory README.md** — For content specific to a single directory. When a user browses into `backend/`, `frontend/`, or `docker/` on GitHub, the README.md renders automatically below the file listing.

- `backend/README.md` — Backend stack, setup, project structure, database schema, migrations, testing
- `frontend/README.md` — Frontend stack, setup, project structure, component library, auth flow
- `docker/README.md` — Compose variants, Dockerfiles, service topology, ports, volumes

**Cross-cutting `docs/`** — For topics that span multiple directories or concern the project as a whole:

- `docs/architecture.md` — System overview, service diagram, directory tree, data flow, model categories
- `docs/deployment.md` — Docker Compose quickstart, environment variables, ports, GPU VPC notes
- `docs/api.md` — API endpoints, authentication, response shapes, pagination, caching

### Where NOT to Put Documentation

- Never put human-readable documentation in `.github/instructions/` — those are agent instructions only.
- Never duplicate content across multiple README files. Link to docs/ instead.
- Never put coding rules or conventions in README files — those belong in `.github/instructions/*.instructions.md`.

## Writing README.md Files

### Structure

Follow this order (omit sections that don't apply):

1. **Title** — Directory/project name as H1
2. **One-liner** — What this directory contains (1-2 sentences)
3. **Stack** — Key technologies (for top-level directories)
4. **Getting Started** — Setup commands to get running locally
5. **Project Structure** — Annotated tree of key files/folders
6. **Key Concepts** — Domain-specific explanations (schemas, auth flow, etc.)
7. **Development** — Common dev tasks (running tests, adding deps, migrations)

### Rules

- Start with a clear H1 title matching the directory purpose, not the tool name.
  - Good: `# Backend` — Bad: `# Python + FastAPI + SQLAlchemy`
  - Good: `# Frontend` — Bad: `# React + TypeScript + Vite + shadcn/ui`
- Keep the first paragraph under 2 sentences. A reader should know what this directory does in 5 seconds.
- Use fenced code blocks with language hints for all commands and code.
- Use tables for structured reference data (schemas, env vars, ports).
- Use relative links to reference other docs: `See [deployment](../docs/deployment.md)`.
- Keep line length reasonable (no hard wrap, but avoid extremely long lines).

## Writing `docs/` Files

### Rules

- One topic per file. Don't create a single massive `docs/README.md`.
- File names: lowercase, hyphen-separated, descriptive — `deployment.md`, `api.md`, `architecture.md`.
- Include a clear H1 title and brief intro paragraph.
- Use diagrams (ASCII art or Mermaid) for architecture and data flow.
- Keep tables for reference data; use prose for explanations.
- Cross-reference related docs with relative links.

## Updating Documentation

After making code changes:

1. **Touched one directory?** Update that directory's README.md if the change affects setup, structure, or key concepts.
2. **Changed cross-cutting behavior?** Update the relevant file in `docs/` (e.g., new env var → `docs/deployment.md`, new endpoint → `docs/api.md`).
3. **Changed project structure?** Update `docs/architecture.md` directory tree.
4. **Never update agent instructions files** (`.github/instructions/`) as part of a feature change — those are maintained separately.
5. **Root README.md** only needs updating for user-facing quickstart changes (new setup steps, changed URLs, etc.).

## Things to Avoid

- Stale docs are worse than no docs. Delete documentation for removed features.
- Don't document implementation details that change frequently — document the *why* and the *interface*.
- Don't use screenshots for CLI output — use code blocks so they're searchable and updatable.
- Don't add "Last updated" dates — use git history for that.
- Don't create `docs/README.md` as a table of contents — the file listing in `docs/` is the TOC.
