# Mulino — Documentation

Mulino is a neighborhood pizzeria web app. It has two surfaces: a public
homepage where diners browse the menu and find the place, and a small
cookie-gated admin area where the owner manages the pizza catalogue. It is
deliberately not a delivery platform or a reservation system — it is a door
into the restaurant.

The codebase is a monorepo with two independent deployable units. The
**frontend** is a Next.js 16 app (App Router, TypeScript). The **backend**
is a FastAPI service (Python 3.12) backed by PostgreSQL, organised in
DDD-lite layers. The two communicate over HTTP only and never import from
each other's source tree; in the browser they share an origin via a Next.js
rewrite, so no CORS configuration is needed.

Everything is built test-first. The backend has unit tests (pure domain and
application logic) and integration tests against a real Postgres instance;
the frontend uses Vitest with React Testing Library and MSW. Two CI workflows —
`backend-tests` and `frontend-tests` — gate every pull request, and `main`
accepts changes through PRs only.

## Index

- [Architecture](./architecture.md) — layers, monorepo layout, stack choices.
- [Domain model](./domain-model.md) — the Pizza aggregate, Money, Allergen, Owner, and invariants.
- [Roadmap](./roadmap.md) — what is built and what remains.
- [Development](./development.md) — setup, commands, and the branch/PR workflow.
- [CI](./ci.md) — how the test workflows ship alongside the code they test.
