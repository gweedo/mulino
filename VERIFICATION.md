# Verification log

End-to-end verification performed on 2026-06-01 against the devcontainer
(Node 20 + Python 3.12 + Postgres 16).

## Backend
- `ruff check .` — clean.
- `pytest` — 129 passed (unit + integration against `pizzeria_test`).
- `alembic upgrade head` — applied cleanly to `pizzeria_dev`.
- `seed_owner` / `seed_pizzas` — idempotent, owner + 7 pizzas present.
- `GET /api/pizzas` — 200, returns only `available=true` pizzas.
- `POST /api/auth/login` — 200, sets httpOnly `session` cookie.

## Frontend
- `lint` — clean.
- `types:gen` — `src/lib/api-types.ts` in sync with the backend OpenAPI schema.
- `test:run` — 22 passed (Vitest + RTL + MSW).
- `build` — production build succeeds.
- Homepage served at `:3000`; `/api/*` rewrite reaches the backend same-origin.

## End-to-end (admin CRUD)
Login → create pizza → mark unavailable → edit → delete, all via the
admin API behind the session cookie. Unavailable pizzas correctly drop
out of the public `/api/pizzas` list; deleted pizzas are gone from the
admin list.

## PR flow
- Direct `git push origin main` is rejected by branch protection.
- Changes land via PR; required status checks (`backend-tests`,
  `frontend-tests`) gate merges to `main`.
