# pizzeria-mulino backend

FastAPI + PostgreSQL backend, DDD-lite layering: `domain → application → infrastructure → api`.

## Quickstart (inside the devcontainer)

```bash
cd backend
uv sync                                                 # installs deps from uv.lock
uv run alembic upgrade head                             # creates pizzas + owners tables
uv run uvicorn pizzeria.api.main:app --reload          # serves http://localhost:8000  (step 09)
```

Environment: the devcontainer exposes Postgres at `db:5432` (user `postgres`, pwd `postgres`, db `pizzeria_dev`). The default `DATABASE_URL` set in `.devcontainer/docker-compose.yml` points at it.

## Tests

```bash
uv run pytest                            # all (unit + integration)
uv run pytest tests/unit                 # unit only (no DB)
uv run pytest tests/integration          # integration (requires Postgres at $DATABASE_URL)
uv run pytest -k test_create_pizza       # single test
uv run ruff check .                      # lint
```

The integration suite auto-creates `pizzeria_test` if it doesn't exist, then runs `alembic upgrade head` once per test session. Each test runs inside a SAVEPOINT that is rolled back at teardown — no state leaks between tests.

Set `DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/pizzeria_test` to target the dedicated test database (CI does this automatically).

## Migrations

```bash
uv run alembic revision --autogenerate -m "<msg>"
uv run alembic upgrade head
uv run alembic downgrade -1
```

`alembic/env.py` reads `DATABASE_URL` from `pizzeria.infrastructure.settings.Settings`, so the same env var drives the app, the tests, and migrations alike.

## Layers

- `domain/` — pure Python, no framework imports. `Allergen`, `Money`, `Pizza`, `Owner`.
- `application/` — use cases over abstract `PizzaRepository` / `OwnerRepository` Protocols. No SQLAlchemy, no FastAPI.
- `infrastructure/` — SQLAlchemy models, `Sql*Repository`, mappers, settings. Also `InMemoryPizzaRepository` (first-class fake usable from tests, CLI dry-runs, or doc snippets).
- `api/` — FastAPI routers + Pydantic schemas (step 09).
