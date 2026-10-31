# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

Monorepo with two independent deployable units:

- `frontend/` — Next.js 14+ (App Router, TypeScript). Public homepage + cookie-gated `/admin` area.
- `backend/` — FastAPI (Python 3.12). DDD-lite layering: `domain → application → infrastructure → api`.
- `.devcontainer/` — polyglot dev container (Node 20 + Python 3.12 + Postgres 16 service).
- `.github/workflows/` — `backend-tests` and `frontend-tests` CI jobs; both must pass before any PR merges to `main`.

Frontend and backend communicate over HTTP only. Neither imports from the other's source tree.

## Git workflow

`main` is branch-protected. All changes go through a PR. Never push directly to `main`.

Branch naming: `feat/<slug>`, `fix/<slug>`, `chore/<slug>`.

## Backend (FastAPI + Python)

**Setup (inside devcontainer or with Postgres running):**
```bash
cd backend
uv sync
uv run alembic upgrade head
uv run python -m pizzeria.seed_pizzas          # optional: seed 7 sample pizzas
uv run uvicorn pizzeria.api.main:app --reload   # http://localhost:8000
```

**Dev login:** there are no local credentials — log in with a user of the dev Supabase project that has `app_metadata.role = "menu_manager"` (see project setup below).
- `seed_pizzas` is idempotent — safe to re-run; skips existing names.

**Tests:**
```bash
cd backend
uv run pytest                        # all tests
uv run pytest tests/unit             # unit only (no DB needed)
uv run pytest tests/integration      # requires Postgres (auto-creates pizzeria_test if missing)
uv run pytest -k test_create_pizza   # single test
uv run ruff check .                  # lint
```

The integration suite auto-creates `pizzeria_test` on first run, applies `alembic upgrade head` once per session, and wraps each test in a SAVEPOINT that is rolled back at teardown — no manual DB setup needed.

**Layer rules (enforce strictly):**
- `domain/` — pure Python, no framework imports. Pizza aggregate, Money and Allergen value objects, `MenuManager`.
- `application/` — use cases only. Depends on the abstract `PizzaRepository` Protocol. No SQLAlchemy, no FastAPI.
- `infrastructure/` — SQLAlchemy models, `SqlPizzaRepository`, Supabase token verification (`security/supabase_jwt.py`). Implements `application/` ports.
- `api/` — FastAPI routers, Pydantic schemas, dependency wiring. Calls use cases; never touches domain directly. **No CORS** — the frontend reaches the backend through a Next.js rewrite (same-origin from the browser). The backend sets no cookies; the Supabase session cookies (set by Next.js) are `httpOnly`, `SameSite=Lax`, `Secure` only over HTTPS.

**API endpoints (conventions, see step 09):**
- Public pizza routes (`GET /api/pizzas`, `GET /api/pizzas/{id}`) return only `available=true`.
- Admin pizza routes are namespaced under `/api/admin/pizzas` (no `?all=true` query flag).
- There are **no `/api/auth/*` routes**: login lives in Supabase Auth (ADR 0001). Admin routes require `Authorization: Bearer <Supabase access token>`; `api/deps.py` verifies it against the project JWKS (ES256/RS256, aud `authenticated`, iss `<SUPABASE_URL>/auth/v1`) and requires `app_metadata.role == "menu_manager"` (401 no/invalid/expired token, 403 wrong role; ADR 0003). Never authorize from `user_metadata`.
- Tests sign tokens with a local ES256 key (`tests/_auth.py`) and override the `get_key_source` dependency — no network, no Supabase in CI.

**DB / migrations:**
App tables live in the private `pizzeria` schema (`MetaData(schema="pizzeria")`), never exposed by Supabase's Data API (ADR 0002). `alembic/env.py` only autogenerates for that schema. Migrations and seeds only need `DATABASE_URL` (`DatabaseSettings`).
```bash
uv run alembic revision --autogenerate -m "<msg>"
uv run alembic upgrade head
uv run alembic downgrade -1
```

**Supabase project setup (once per environment — dashboard settings, not in the repo; full walkthrough in `docs/supabase-setup.md`):**

1. Create the Supabase project.
2. Auth → JWT signing keys: switch to **asymmetric keys** (ES256). FastAPI verifies tokens via the project's JWKS and rejects the legacy shared secret.
3. Data API: switch **"Enable Data API" off**, and never add `pizzeria` to the exposed schemas (ADR 0002).
4. Auth → Sign In / Providers: disable **"Allow new users to sign up"**.
5. Auth → Users → Add user → Create new user (email + password, auto-confirm), then grant the role:
   `UPDATE auth.users SET raw_app_meta_data = raw_app_meta_data || '{"role": "menu_manager"}' WHERE email = '<email>';`
   The role is in the token from the next sign-in.

**Production deployment runbook:**
On every deploy, before starting the FastAPI process:

1. `DATABASE_URL=<direct connection> uv run alembic upgrade head` — apply pending schema migrations over the **direct** connection.
2. Start `uvicorn pizzeria.api.main:app` with `DATABASE_URL` set to the direct connection or the **session-mode pooler (port 5432)**. Never the transaction-mode pooler (6543): asyncpg needs prepared statements.

Step 1 must complete before step 2 to avoid serving traffic against a stale schema.

**Lost password (interim, until in-app recovery ships):** a Menu Manager deletes the user in Supabase → Auth → Users, recreates it (setup step 5), and grants `menu_manager` again.

**Environment variables (backend):**
`DATABASE_URL`, `SUPABASE_URL` (e.g. `https://<ref>.supabase.co`; the JWT issuer and JWKS URL derive from it). See `backend/.env.example`.

## Frontend (Next.js + TypeScript)

**Setup:**
```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

**Tests:**
```bash
npm test             # vitest watch mode
npm run test:run     # single run (used in CI)
npm run lint         # eslint
npm run build        # production build check
```

**Next.js 16 breaking changes (vs. your training data):**
- `middleware.ts` → **`proxy.ts`**. The file is `src/proxy.ts` and exports `export function proxy(...)`. The word "middleware" no longer exists in Next.js 16 — it is called **Proxy**. Do not create or reference `middleware.ts`.

**Key conventions:**
- `src/lib/api.ts` — typed HTTP client wrapping `fetch` with `credentials: 'include'`. Uses relative URLs (`/api/...`) — same-origin via the Next.js rewrite. All API calls go through here.
- `src/lib/api-types.ts` is **generated** from the backend's `/openapi.json` via `npm run types:gen` (uses `openapi-typescript`). `src/lib/types.ts` only re-exports / narrows the generated types. CI fails if `api-types.ts` is out of date.
- Homepage (`src/app/page.tsx`) is a Next.js Server Component that fetches with `{ next: { tags: ['pizzas'], revalidate: 60 } }`. Admin create/edit/delete server actions call `revalidateTag('pizzas')` so edits show up immediately; the 60s ISR window is the fallback.
- Admin routes (`src/app/admin/`) are gated by `src/proxy.ts`, which refreshes the Supabase session and redirects when `supabase.auth.getClaims()` finds no verified session. It is a convenience, not the security boundary — FastAPI checks every request.
- Supabase session: `src/lib/supabase/server.ts` (`createSupabaseServerClient`, `authHeader`). Server-side only — never create a browser Supabase client. Cookies are forced `httpOnly` (`src/lib/supabase/config.ts`; `@supabase/ssr` defaults to `false`). Only the proxy refreshes sessions.
- Login/logout are server actions in `src/app/admin/actions.ts` (`signInWithPassword` behind a 5/min/IP in-memory limiter; `signOut({ scope: 'local' })`). Admin fetches send `Authorization: Bearer` via `authHeader()`.
- Tests live in `src/__tests__/` and use Vitest + React Testing Library + MSW for API mocking.

**Environment variables (frontend):**
`BACKEND_INTERNAL_URL` (e.g. `http://localhost:8000`), `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` — all consumed only by the Next.js server process. The browser always talks to the frontend origin; `next.config.ts` rewrites `/api/*` to `BACKEND_INTERNAL_URL/api/*`. `NEXT_PUBLIC_*` variables are **not** used. See `frontend/.env.example`.

## Domain model (Pizza aggregate)

Fields: `id`, `name` (unique ≤80 chars), `description`, `ingredients` (≥1), `allergens` (subset of EU 14 enum), `price` (Money value object, amount > 0), `available`.

EU 14 allergens: `gluten crustaceans eggs fish peanuts soy milk nuts celery mustard sesame sulphites lupin molluscs`.

Invariants are enforced in `backend/src/pizzeria/domain/` — never in the API or DB layer.

**MenuManager**: frozen dataclass `MenuManager(id, email)` in `backend/src/pizzeria/domain/menu_manager.py`, built from a verified Supabase token (`id` = `sub`). Anyone allowed to change the Menu — today the owner, later possibly staff. There is no owners table. Vocabulary lives in `CONTEXT.md`; decisions in `docs/adr/`.

## TDD discipline

Red → green → refactor on every change. The test file for a module is written before the implementation. Unit tests use `InMemoryPizzaRepository` (defined in `tests/unit/application/fakes.py`); integration tests hit a real Postgres instance.

## Contacts (hardcoded)

The public homepage contacts section uses the fixed pizzeria data from https://maps.app.goo.gl/DB4NzLKxTB1yXaxaA. Do not add a contacts admin UI — those values live in `src/components/Contacts.tsx`.
