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
  the Money and Allergen value objects and `MenuManager`. All
  business invariants live here.
- **application** — use cases only. They depend on abstract repository
  *protocols* (`PizzaRepository`), never on SQLAlchemy
  or FastAPI.
- **infrastructure** — concrete implementations: SQLAlchemy models and
  repositories, Alembic migrations, and Supabase access-token verification
  (JWKS). App tables live in the private `pizzeria` schema.
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
- `src/proxy.ts` — refreshes the Supabase session and redirects `/admin/*`
  visitors without a verified one (`getClaims()`). (In Next.js 16 this file is
  `proxy.ts`, not `middleware.ts`; the export is `export function proxy(...)`.)
- `src/lib/supabase/` — server-only Supabase client; session cookies are
  forced `httpOnly`.

## Authentication (Supabase)

Supabase Auth signs Menu Managers in and issues tokens; FastAPI decides access
(see [ADR 0001](./adr/0001-supabase-for-database-and-auth.md)).

1. The login form calls a Next.js server action, which signs in with
   `@supabase/ssr`; the session lands in httpOnly cookies.
2. Admin server actions and pages read the access token and send it to
   FastAPI as `Authorization: Bearer`.
3. FastAPI verifies it against the project's JWKS and requires
   `app_metadata.role = "menu_manager"`
   ([ADR 0003](./adr/0003-menu-manager-role-claim.md)).

Supabase's Data API is switched off and app tables live in a private schema,
so FastAPI is the only way into the data
([ADR 0002](./adr/0002-no-supabase-data-api.md)).

## Same-origin API

The browser always talks to the frontend origin. `next.config.ts` rewrites
`/api/*` to the backend (`BACKEND_INTERNAL_URL`). Because requests are
same-origin from the browser's perspective, the backend sets **no CORS
headers**. The Supabase session cookies are `httpOnly`, `SameSite=Lax`, and
`Secure` only over HTTPS.

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
