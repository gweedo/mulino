# Verification log

End-to-end verification performed on 2026-06-01 against the devcontainer
(Node 20 + Python 3.12 + Postgres 16).

## Backend

- `ruff check .` — clean.
- `pytest` — 129 passed (unit + integration against `pizzeria_test`).
- `alembic upgrade head` — applied cleanly to `pizzeria_dev`.
- `seed_owner` / `seed_pizzas` — idempotent; owner + 7 sample pizzas present.
- `GET /api/pizzas` — 200, returns only `available=true` pizzas (6 of 7 seeded).
- `POST /api/auth/login` — 200, sets httpOnly `session` cookie (`SameSite=lax`).

## Frontend

- `lint` — clean (ESLint, 0 errors/warnings).
- `types:gen` — `src/lib/api-types.ts` in sync with the committed `openapi.json`.
- `test:run` — 22 passed (Vitest + React Testing Library + MSW).
- `build` — production build succeeds (TypeScript + Turbopack, 0 errors).
- Homepage served at `:3000`; `/api/*` rewrite reaches the backend same-origin (no CORS).

## End-to-end (admin CRUD)

Scripted flow using `curl` with a cookie jar against `http://localhost:8000`:

| Step | HTTP | Result |
|------|------|--------|
| `POST /api/auth/login` | 200 | httpOnly session cookie set |
| `GET /api/auth/me` | 200 | returns `owner@example.com` |
| `POST /api/pizzas` (available=true) | 201 | pizza created with UUID |
| `GET /api/pizzas` | 200 | new pizza present in public list |
| `PUT /api/pizzas/:id` (available=false) | 204 | pizza marked unavailable |
| `GET /api/pizzas` | 200 | pizza no longer in public list |
| `DELETE /api/pizzas/:id` | 204 | pizza deleted |
| `GET /api/admin/pizzas` | 200 | pizza gone from admin list |

All assertions passed. No `BAD` or `STILL-PRESENT` markers.

## PR flow

- Direct `git push origin main` is rejected by branch protection.
- Changes land via pull request; required status checks gate merges to `main`.
- Branch protection updated: both `backend-tests` and `frontend-tests` are
  now required status checks (previously only `backend-tests` was required).
