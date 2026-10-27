# Development

[← Back to docs index](./README.md)

## Getting started

Open the repository in VS Code and choose **Reopen in Container**. The
devcontainer provides Node 20, Python 3.12, and a PostgreSQL 16 service
reachable at host `db`.

## Backend

```bash
cd backend
uv sync                        # install dependencies
uv run alembic upgrade head    # apply migrations
uv run python -m pizzeria.seed_pizzas          # optional: 7 sample pizzas
uv run uvicorn pizzeria.api.main:app --reload  # http://localhost:8000
```

The backend reads `DATABASE_URL` (e.g.
`postgresql+asyncpg://postgres:postgres@db:5432/pizzeria_dev`) and
`SUPABASE_URL` from the environment or `backend/.env` (see
`backend/.env.example`). Migrations and seeds need only `DATABASE_URL`.

**Logging in locally:** login goes to a free "dev" Supabase project. Put its
URL and publishable key in `frontend/.env.local` (see `frontend/.env.example`)
and its URL in `backend/.env`, then sign in with a dev-project user that has
the `menu_manager` role. Tests and CI never talk to Supabase.

**Supabase project setup (once per environment — dashboard settings, not in the repo):**

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

**Tests and linting:**

```bash
cd backend
uv run pytest                    # all tests (unit + integration)
uv run pytest tests/unit         # unit only (no DB needed)
uv run pytest tests/integration  # requires Postgres
uv run ruff check .              # lint
```

The integration suite auto-creates `pizzeria_test`, applies migrations once
per session, and wraps each test in a rolled-back savepoint — no manual DB
setup needed.

## Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
npm run lint
npm run test:run     # single run (used in CI)
npm run build        # production build check
npm run types:gen    # regenerate src/lib/api-types.ts from ../openapi.json
```

The frontend reaches the backend through a same-origin rewrite, so the
browser only ever talks to `http://localhost:3000`. Set
`BACKEND_INTERNAL_URL` if the backend runs elsewhere (default:
`http://localhost:8000`).

## Branch and PR workflow

`main` is branch-protected and accepts changes through pull requests only.
Branch names follow `feat/<slug>`, `fix/<slug>`, or `chore/<slug>`. Both
`backend-tests` and `frontend-tests` must pass before a PR can merge. See
[CI](./ci.md) for details.

## API types

`src/lib/api-types.ts` is generated from the committed `openapi.json` at
the repo root. Regenerate it after changing any backend schema:

```bash
# From repo root — generate the schema from FastAPI without a live server:
cd backend && uv run python -c \
  "from pizzeria.api.main import app; import json; print(json.dumps(app.openapi(), indent=2))" \
  > ../openapi.json

# Then regenerate the TypeScript types:
cd frontend && npm run types:gen
```

CI will fail if `api-types.ts` is out of sync with `openapi.json`.
