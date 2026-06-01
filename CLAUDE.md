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
OWNER_EMAIL=owner@example.com OWNER_PASSWORD=secret uv run python -m pizzeria.seed_owner
uv run uvicorn pizzeria.api.main:app --reload   # http://localhost:8000
```

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
- `domain/` — pure Python, no framework imports. Pizza aggregate, Money and Allergen value objects (Owner value object lands in step 08).
- `application/` — use cases only. Depends on abstract `PizzaRepository` and `OwnerRepository` Protocols. No SQLAlchemy, no FastAPI.
- `infrastructure/` — SQLAlchemy models, `SqlPizzaRepository`, JWT/password helpers. Implements `application/` ports.
- `api/` — FastAPI routers, Pydantic schemas, dependency wiring. Calls use cases; never touches domain directly. **No CORS** — the frontend reaches the backend through a Next.js rewrite (same-origin from the browser). Cookies: `httpOnly`, `SameSite=Lax`, `Secure` set only when the request is HTTPS.

**API endpoints (conventions, see step 09):**
- Public pizza routes (`GET /api/pizzas`, `GET /api/pizzas/{id}`) return only `available=true`.
- Admin pizza routes are namespaced under `/api/admin/pizzas` (no `?all=true` query flag).
- `POST /api/auth/login` is rate-limited via `slowapi` to 5 req/min/IP and sets the `session` cookie. `POST /api/auth/logout` clears it. `GET /api/auth/me` returns the current owner.

**DB / migrations:**
Alembic ships in step 07 (alongside the SQLAlchemy models), not step 10. Step 10 only owns the owner seed script + the production migration runbook.
```bash
uv run alembic revision --autogenerate -m "<msg>"
uv run alembic upgrade head
uv run alembic downgrade -1
```

**Production deployment runbook:**
On every deploy, before starting the FastAPI process:

1. `uv run alembic upgrade head` — apply pending schema migrations.
2. `OWNER_EMAIL=… OWNER_PASSWORD=… uv run python -m pizzeria.seed_owner` —
   first deploy only; safe to re-run (no-op if owner exists).
3. Password rotation / lost-password recovery:
   `OWNER_EMAIL=… OWNER_PASSWORD=newpass OWNER_FORCE_RESET=1 uv run python -m pizzeria.seed_owner`
4. Start `uvicorn pizzeria.api.main:app`.

Step 1 must complete before step 4 to avoid serving traffic against a stale schema.

**Environment variables (backend):**
`DATABASE_URL`, `JWT_SECRET`, `JWT_ALG` (default HS256), `JWT_TTL_MIN` (default 120), `OWNER_EMAIL`, `OWNER_PASSWORD`. Optional: `OWNER_FORCE_RESET=1` makes `python -m pizzeria.seed_owner` overwrite an existing owner's `password_hash` (used for rotation / lost-password recovery).

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

**Key conventions:**
- `src/lib/api.ts` — typed HTTP client wrapping `fetch` with `credentials: 'include'`. Uses relative URLs (`/api/...`) — same-origin via the Next.js rewrite. All API calls go through here.
- `src/lib/api-types.ts` is **generated** from the backend's `/openapi.json` via `npm run types:gen` (uses `openapi-typescript`). `src/lib/types.ts` only re-exports / narrows the generated types. CI fails if `api-types.ts` is out of date.
- Homepage (`src/app/page.tsx`) is a Next.js Server Component that fetches with `{ next: { tags: ['pizzas'], revalidate: 60 } }`. Admin create/edit/delete server actions call `revalidateTag('pizzas')` so edits show up immediately; the 60s ISR window is the fallback.
- Admin routes (`src/app/admin/`) are client components gated by `src/proxy.ts` (Next.js 16 renamed middleware to proxy; checks httpOnly `session` cookie).
- Tests live in `src/__tests__/` and use Vitest + React Testing Library + MSW for API mocking.

**Environment variables (frontend):**
`BACKEND_INTERNAL_URL` (e.g. `http://localhost:8000`) — consumed only by the Next.js server process. The browser always talks to the frontend origin; `next.config.mjs` rewrites `/api/*` to `BACKEND_INTERNAL_URL/api/*`. `NEXT_PUBLIC_*` API base is **not** used.

## Domain model (Pizza aggregate)

Fields: `id`, `name` (unique ≤80 chars), `description`, `ingredients` (≥1), `allergens` (subset of EU 14 enum), `price` (Money value object, amount > 0), `available`.

EU 14 allergens: `gluten crustaceans eggs fish peanuts soy milk nuts celery mustard sesame sulphites lupin molluscs`.

Invariants are enforced in `backend/src/pizzeria/domain/` — never in the API or DB layer.

**Owner aggregate** (introduced in step 08): frozen dataclass `Owner(id, email, password_hash)` in `backend/src/pizzeria/domain/owner.py`. The `application/ports/owner_repository.py` Protocol is the abstraction the `AuthenticateOwner` use case depends on — never the SQLAlchemy ORM.

## TDD discipline

Red → green → refactor on every change. The test file for a module is written before the implementation. Unit tests use `InMemoryPizzaRepository` (defined in `tests/unit/application/fakes.py`); integration tests hit a real Postgres instance.

## Contacts (hardcoded)

The public homepage contacts section uses the fixed pizzeria data from https://maps.app.goo.gl/DB4NzLKxTB1yXaxaA. Do not add a contacts admin UI — those values live in `src/components/Contacts.tsx`.
