# Supabase for the database and login, FastAPI kept

We moved the database to Supabase Postgres and login to Supabase Auth, but kept FastAPI and its domain layer so pizza invariants stay in Python. Next.js manages the Supabase session with `@supabase/ssr` (httpOnly cookies, refreshed in `src/proxy.ts`) and sends the access token to FastAPI as an `Authorization: Bearer` header; FastAPI only verifies it against Supabase's JWKS.

## Considered Options

- **FastAPI brokers login** (calls Supabase's password grant, sets its own cookie) — rejected: we would hand-write refresh-token rotation and the OAuth/PKCE callback for social login, off Supabase's documented path.
- **Drop FastAPI** for supabase-js + Row Level Security — rejected: moves the pizza invariants out of the domain layer.

## Consequences

`src/proxy.ts` is a redirect convenience, never the security boundary: FastAPI checks the token on every admin request.
