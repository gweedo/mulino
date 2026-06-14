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
# seed the single owner (idempotent):
OWNER_EMAIL=owner@example.com OWNER_PASSWORD=secret uv run python -m pizzeria.seed_owner
uv run python -m pizzeria.seed_pizzas          # optional: 7 sample pizzas
uv run uvicorn pizzeria.api.main:app --reload  # http://localhost:8000
```

The backend reads `DATABASE_URL` (e.g.
`postgresql+asyncpg://postgres:postgres@db:5432/pizzeria_dev`) and
`JWT_SECRET` from the environment. After seeding, log in with
`owner@example.com` / `secret`.

**Password rotation / lost-password recovery:**

```bash
OWNER_EMAIL=owner@example.com OWNER_PASSWORD=newpass OWNER_FORCE_RESET=1 \
  uv run python -m pizzeria.seed_owner
```

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
