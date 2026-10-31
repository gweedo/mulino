# Roadmap

[← Back to docs index](./README.md)

This file is the canonical record of build progress. ✅ = landed on `main`;
⬜ = not yet started.

## Backend

- ✅ Repository scaffold and devcontainer (Node 20 + Python 3.12 + Postgres 16).
- ✅ Backend bootstrap — `uv` setup, DDD package skeleton, `backend-tests` CI workflow.
- ✅ Domain layer — Pizza aggregate, Money and Allergen value objects (TDD).
- ✅ Application layer — five use cases (list, get, create, update, delete) against repository protocols (TDD).
- ✅ Infrastructure layer — SQLAlchemy async models, repositories, Alembic migrations, SAVEPOINT test isolation (TDD).
- ✅ Auth layer — Argon2 password hashing, JWT httpOnly cookie, `AuthenticateOwner` use case, rate-limited login (TDD).
- ✅ API layer — FastAPI routers wiring every use case; env-aware `Secure` cookie flag (TDD).
- ✅ Owner seed script — idempotent, supports `OWNER_FORCE_RESET=1`; production deployment runbook.
- ✅ Supabase migration — Supabase Postgres (private `pizzeria` schema, Data API off) and Supabase Auth; FastAPI verifies JWTs via JWKS and a `menu_manager` role; owners table, Argon2, JWT minting and `seed_owner` removed (ADRs 0001–0003).

## Frontend

- ✅ Frontend bootstrap — Next.js 16, Vitest + RTL + MSW, `frontend-tests` CI workflow.
- ✅ Typed API client — `openapi-typescript` generated types; CI drift check.
- ✅ Public homepage — Server Component with ISR (60 s revalidate + tag-based invalidation).
- ✅ Admin login — server action sets httpOnly cookie; `src/proxy.ts` gates `/admin/*`.
- ✅ Supabase session — `@supabase/ssr` server-side only, httpOnly cookies, Bearer token to FastAPI, login rate limit in the server action.
- ✅ Admin CRUD dashboard — list, create, edit, delete; server actions call `revalidateTag`.

## Project-wide

- ✅ End-to-end verification — all backend and frontend checks pass; scripted admin CRUD e2e confirmed.
- ✅ Tracked documentation — this `docs/` tree + `scripts/refresh-docs.sh`.

## Out of scope (future work)

- ⬜ Password recovery in the app (`/auth/confirm`, forgot/update password) — to be decided in a dedicated grilling session. Interim: recreate the user in the Supabase dashboard.

- ⬜ Social login (Google, Microsoft, Apple) — tracked in GitHub issue #14.
- ⬜ Production hosting and secrets management.
- ⬜ Release-pipeline migrations and observability (logs, error reporting, uptime monitoring).
