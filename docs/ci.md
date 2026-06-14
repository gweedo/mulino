# Continuous integration

[← Back to docs index](./README.md)

Two GitHub Actions workflows guard the repository:

- **`backend-tests`** — spins up a PostgreSQL 16 service, installs the
  backend with `uv`, runs `ruff check .`, then `pytest` (unit +
  integration). Defined in `.github/workflows/backend.yml`.
- **`frontend-tests`** — installs the frontend with `npm ci`, runs the
  ESLint linter, checks that the generated API types are in sync with
  `openapi.json`, runs the Vitest suite (unit + MSW handler tests), and
  performs a production build. Defined in `.github/workflows/frontend.yml`.

Both run on every pull request and on pushes to `main`. Both are required
status checks — a PR cannot merge until both are green.

## Workflows ship with the code they test

Each workflow was introduced in the same pull request that bootstrapped the
stack it covers:

- `backend-tests` arrived with the backend bootstrap (step 4, PR #4).
- `frontend-tests` arrived with the frontend bootstrap (step 11, PR #10).

A stack is never added without its test job landing alongside it. This means
`main` has been green from the first commit of every component, and there is
never a window where code exists without CI coverage.

This principle required a small workaround during the early frontend CI job
(before `frontend/package.json` existed): a guard step skipped all
frontend-specific checks until the scaffold was present. Step 11 removed
that guard and replaced it with a full `npm ci` + lint + test + build run.

## Required status checks

`main` is branch-protected with these rules:

- Direct pushes are rejected.
- Force pushes are blocked.
- Both `backend-tests` and `frontend-tests` must report success before a
  PR can merge.

To verify the current protection rules:

```bash
gh api repos/{owner}/mulino/branches/main/protection/required_status_checks \
  --jq '.contexts'
```
