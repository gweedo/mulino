# Architecture

[← Back to docs index](./README.md)

## Monorepo layout

```
frontend/   Next.js 16 app — public homepage + cookie-gated /admin area
backend/    FastAPI service — domain, application, infrastructure, api layers
.github/    CI workflows (backend-tests, frontend-tests)
docs/       This documentation
scripts/    Maintenance scripts (refresh-docs.sh)
```

The frontend and backend are independently deployable and communicate over
HTTP only. Neither imports from the other's source tree.

## Backend layering (DDD-lite)

The backend is split into four layers with a strict one-way dependency rule:
`domain → application → infrastructure → api`.

- **domain** — pure Python, no framework imports. The Pizza aggregate plus
  the Money and Allergen value objects and the Owner value object. All
  business invariants live here.
- **application** — use cases only. They depend on abstract repository
  *protocols* (`PizzaRepository`, `OwnerRepository`), never on SQLAlchemy
  or FastAPI.
- **infrastructure** — concrete implementations: SQLAlchemy models and
  repositories, Alembic migrations, JWT and password-hashing helpers.
- **api** — FastAPI routers, Pydantic schemas, and dependency wiring. The
  API layer calls use cases and never reaches into the domain directly.

## Frontend structure

- `src/app/` — App Router pages. The homepage (`page.tsx`) is a Server
  Component that fetches pizzas with ISR (60 s revalidate + tag-based
  invalidation). `/admin/*` pages are client components.
- `src/lib/api.ts` — a typed `fetch` wrapper using relative `/api/...`
  URLs and `credentials: 'include'`. All browser-side API calls go through it.
- `src/lib/api-types.ts` — generated from the backend's OpenAPI schema via
  `npm run types:gen`; CI fails if it drifts from the committed schema.
- `src/proxy.ts` — guards `/admin/*` routes by checking the httpOnly
  `session` cookie. (In Next.js 16 this file is `proxy.ts`, not
  `middleware.ts`; the export is `export function proxy(...)`.)

## Same-origin API

The browser always talks to the frontend origin. `next.config.ts` rewrites
`/api/*` to the backend (`BACKEND_INTERNAL_URL`). Because requests are
same-origin from the browser's perspective, the backend sets **no CORS
headers**. The auth cookie is `httpOnly`, `SameSite=Lax`, and `Secure` only
over HTTPS.

## Stack

| Concern         | Choice                                              |
|-----------------|-----------------------------------------------------|
| Frontend        | Next.js 16, React, TypeScript                       |
| Frontend tests  | Vitest + React Testing Library + MSW                |
| Backend         | FastAPI, Python 3.12                                |
| Backend tools   | uv, ruff, pytest                                    |
| ORM / migrations| SQLAlchemy (async) + Alembic                        |
| Auth            | JWT in an httpOnly cookie; rate-limited login       |
| Database        | PostgreSQL 16                                       |
| Dev environment | Polyglot devcontainer (Node 20 + Python 3.12 + Postgres 16) |
