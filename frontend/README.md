# Frontend

React single-page application for ModelServe. Provides a dashboard for viewing configured model slots, their health status, API key management, and copy-paste OpenAI SDK scripts for served models.

## Stack

- **React 18** with **TypeScript** (strict mode)
- **Vite** build tool
- **shadcn/ui** component library
- **TanStack Query** for server state management
- **Sonner** for toast notifications

---

## Getting Started

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev          # http://localhost:5173

# Type check
npm run typecheck    # tsc --noEmit

# Lint
npm run lint         # eslint + biome
```

---

## Project Structure

```text
frontend/
├── src/
│   ├── App.tsx               # Root component, routing
│   ├── main.tsx              # Entry point
│   ├── index.css             # Global styles + Tailwind
│   ├── components/
│   │   ├── ui/               # shadcn generated components (DO NOT hand-edit)
│   │   ├── app/              # App-specific composed components
│   │   │   ├── layout.tsx    # App shell layout
│   │   │   ├── model-card.tsx
│   │   │   ├── env-snippet.tsx
│   │   │   ├── serve-script-dialog.tsx
│   │   │   ├── status-badge.tsx
│   │   │   └── protected-route.tsx
│   │   ├── login-form.tsx
│   │   └── signup-form.tsx
│   ├── pages/                # Route-level page components
│   │   ├── models.tsx        # Configured model slots (public)
│   │   ├── served.tsx        # Served models dashboard (authed)
│   │   ├── keys.tsx          # API key management
│   │   ├── login.tsx
│   │   └── signup.tsx
│   ├── hooks/                # Custom React hooks + TanStack Query hooks
│   │   ├── useAuth.ts
│   │   ├── useModels.ts      # useConfiguredModels() — polls GET /models
│   │   ├── useServe.ts       # useServedModels() — polls GET /serve
│   │   └── useKeys.ts
│   ├── lib/
│   │   ├── api.ts            # HTTP client, base URL config
│   │   └── utils.ts          # cn(), formatters
│   └── types/                # Shared TypeScript types
│       ├── api.ts            # DataResponse, ErrorResponse
│       ├── auth.ts
│       ├── keys.ts
│       └── serve.ts          # ServedModel, ModelStatus
├── components.json           # shadcn config
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## Component Library

All UI components come from **shadcn/ui**. Generated components live in `src/components/ui/` and should not be hand-edited.

```bash
# Add a new shadcn component
npx shadcn@latest add dialog
npx shadcn@latest add sonner
```

App-specific compositions (like `ModelCard` and `ServeScriptDialog`) live in `src/components/app/`.

---

## Auth Flow

- Auth pages: `/login` and `/signup`
- Bearer token persisted in localStorage
- `Authorization: Bearer <token>` set via the shared API client in `lib/api.ts`
- App routes protected by `ProtectedRoute` component (validates `/auth/me` via TanStack Query)
- Logout clears local token state and TanStack Query cache
