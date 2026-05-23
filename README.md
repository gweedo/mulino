# mulino

Pizzeria web app — public homepage + owner admin area.

## Layout

- `frontend/` — Next.js (React + TypeScript) public site and admin UI.
- `backend/` — FastAPI + PostgreSQL backend, DDD-lite layering (`domain`, `application`, `infrastructure`, `api`).
- `.devcontainer/` — polyglot dev container (Node 20 + Python 3.12 + Postgres 16).
- `.github/workflows/` — CI: `backend-tests` and `frontend-tests` workflows gate PRs to `main`.

## Workflow

`main` is protected. All changes land via pull request, and both `backend-tests` and `frontend-tests` must pass before merge.

## Quickstart

1. Open this folder in VS Code and "Reopen in Container".
2. Backend: `cd backend && uv sync && uv run alembic upgrade head && uv run uvicorn pizzeria.api.main:app --reload`.
3. Frontend: `cd frontend && npm install && npm run dev`.

See `../.claude/plans/let-me-create-a-expressive-wind.md` for the full implementation plan and per-step YAML chunks.
