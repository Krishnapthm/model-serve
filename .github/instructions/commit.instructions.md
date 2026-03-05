---
name: "Commit Messages"
description: "Conventional Commits format: type(scope): description — lowercase, imperative, ≤ 72 chars"
applyTo: "**"
---

# Commit Message Guidelines

> Based on the [Conventional Commits](https://www.conventionalcommits.org/) specification.

## Format

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

## Rules

### Header

- **type** and **description** are mandatory; **scope** is optional
- Keep the entire header under **72 characters** (ideally ≤ 50)
- Use **lowercase** throughout — no capitalization
- Use **imperative, present tense**: "add" not "added" or "adds"
  - Ask yourself: _"If applied, this commit will…"_
- Do **not** end the description with a period

### Body (optional)

- Separate from the header with a **blank line**
- Explain the **what** and **why**, not the how
- Wrap lines at **72 characters**
- Use imperative, present tense here too

### Footer (optional)

- Separate from the body with a **blank line**
- Reference issues: `Closes #123`, `Fixes JIRA-456`
- Breaking changes **must** start with `BREAKING CHANGE:` on its own line

---

## Types

| Type       | When to use                                                     |
| ---------- | --------------------------------------------------------------- |
| `feat`     | Adds, adjusts, or removes a user-facing feature (API or UI)     |
| `fix`      | Fixes a bug in a previously shipped feature                     |
| `refactor` | Rewrites or restructures code without changing behavior         |
| `perf`     | A refactor specifically aimed at improving performance          |
| `style`    | Whitespace, formatting, missing semicolons — no behavior change |
| `test`     | Adds missing tests or corrects existing ones                    |
| `docs`     | Documentation only changes                                      |
| `build`    | Build tools, dependencies, project version bumps                |
| `ops`      | CI/CD pipelines, deployment scripts, infrastructure (IaC)       |
| `chore`    | Miscellaneous tasks: initial commit, `.gitignore` edits, etc.   |

> **Not sure which type to use?** Use this decision order:
>
> 1. Bug fix? → `fix`
> 2. New/changed user-facing feature? → `feat`
> 3. Performance improvement? → `perf`
> 4. Code restructure without behavior change? → `refactor`
> 5. Formatting only? → `style`
> 6. Tests? → `test`
> 7. Docs? → `docs`
> 8. Build tools / deps? → `build`
> 9. DevOps / infra? → `ops`
> 10. Everything else → `chore`

---

## Breaking Changes

Add `!` before the `:` in the header to flag a breaking change:

```
feat(api)!: remove status endpoint
```

Also add a footer:

```
BREAKING CHANGE: the /status endpoint has been removed. Use /health instead.
```

---

## Scopes

- Optional, but recommended when the codebase has clear modules
- Written in **lowercase**, usually a single word or hyphenated (`shopping-cart`, `auth`, `api`)
- Do **not** use issue IDs as scopes

---

## Special Commits

```
chore: init                        ← initial commit
Merge branch '<branch-name>'       ← merge (use git default)
Revert "<original commit subject>" ← revert (use git default)
```

---

## Examples

```
feat(auth): add OAuth2 login support

fix(cart): prevent checkout with empty cart

fix: add missing parameter to payment service call

The error occurred because the currency code was not forwarded
from the request context to the downstream service.

Closes #88

docs(readme): update local setup instructions

refactor(db): extract query builder into separate module

perf: replace linear scan with binary search for tag lookup

feat(api)!: remove deprecated v1 user endpoint

BREAKING CHANGE: /v1/users is no longer available. Migrate to /v2/users.

chore: init

build: upgrade typescript to 5.4

style: fix inconsistent indentation in auth module

test(payments): add edge case for zero-amount transactions

ops: add health check to docker-compose deployment
```

---

## Anti-patterns to Avoid

- ❌ `fix stuff` — vague, explains nothing
- ❌ `updated code` — passive voice, no context
- ❌ `WIP` — never commit without a meaningful message
- ❌ Bundling unrelated changes in one commit — keep commits atomic
- ❌ Describing _how_ the code works in the message — the code does that

---

## Versioning Impact (SemVer)

| Commit contains         | Version bump              |
| ----------------------- | ------------------------- |
| `BREAKING CHANGE` / `!` | **Major** (1.0.0 → 2.0.0) |
| `feat` or `fix`         | **Minor** (1.0.0 → 1.1.0) |
| Anything else           | **Patch** (1.0.0 → 1.0.1) |
