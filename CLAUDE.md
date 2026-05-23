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
uv run pytest tests/integration      # requires Postgres
uv run pytest -k test_create_pizza   # single test
uv run ruff check .                  # lint
```

**Layer rules (enforce strictly):**
- `domain/` — pure Python, no framework imports. Pizza aggregate, Money and Allergen value objects.
- `application/` — use cases only. Depends on abstract `PizzaRepository` Protocol. No SQLAlchemy, no FastAPI.
- `infrastructure/` — SQLAlchemy models, `SqlPizzaRepository`, JWT/password helpers. Implements `application/` ports.
- `api/` — FastAPI routers, Pydantic schemas, dependency wiring. Calls use cases; never touches domain directly.

**DB / migrations:**
```bash
uv run alembic revision --autogenerate -m "<msg>"
uv run alembic upgrade head
uv run alembic downgrade -1
```

**Environment variables (backend):**
`DATABASE_URL`, `JWT_SECRET`, `JWT_ALG` (default HS256), `JWT_TTL_MIN` (default 120), `OWNER_EMAIL`, `OWNER_PASSWORD`.

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
- `src/lib/api.ts` — typed HTTP client wrapping `fetch` with `credentials: 'include'`. All API calls go through here.
- `src/lib/types.ts` — TypeScript types mirroring backend Pydantic schemas. Keep in sync manually.
- Homepage (`src/app/page.tsx`) is a Next.js Server Component that fetches with `{ next: { revalidate: 60 } }`.
- Admin routes (`src/app/admin/`) are client components gated by `src/middleware.ts` (checks httpOnly `session` cookie).
- Tests live in `src/__tests__/` and use Vitest + React Testing Library + MSW for API mocking.

**Environment variables (frontend):**
`NEXT_PUBLIC_API_BASE_URL` (e.g. `http://localhost:8000`).

## Domain model (Pizza aggregate)

Fields: `id`, `name` (unique ≤80 chars), `description`, `ingredients` (≥1), `allergens` (subset of EU 14 enum), `price` (Money value object, amount > 0), `available`.

EU 14 allergens: `gluten crustaceans eggs fish peanuts soy milk nuts celery mustard sesame sulphites lupin molluscs`.

Invariants are enforced in `backend/src/pizzeria/domain/` — never in the API or DB layer.

## TDD discipline

Red → green → refactor on every change. The test file for a module is written before the implementation. Unit tests use `InMemoryPizzaRepository` (defined in `tests/unit/application/fakes.py`); integration tests hit a real Postgres instance.

## Contacts (hardcoded)

The public homepage contacts section uses the fixed pizzeria data from https://maps.app.goo.gl/DB4NzLKxTB1yXaxaA. Do not add a contacts admin UI — those values live in `src/components/Contacts.tsx`.
