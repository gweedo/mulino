# FastAPI is reached only from the Next.js server

Every call to FastAPI is made server-side by `frontend/src/lib/backend.ts`, from server actions and Server Components, to `BACKEND_INTERNAL_URL`. The browser never calls FastAPI, so the Next.js `/api/*` rewrite was removed. FastAPI need only be reachable from the Next.js server.

The Supabase access token lives in httpOnly cookies that only the Next.js server can read (ADR 0001). Browser-side calls to FastAPI could not carry it, so the rewrite served no app code. It only exposed every FastAPI route on the public frontend origin.

## Considered Options

- **Keep the rewrite** for future browser-side calls. Rejected: these would need the token in JavaScript, which goes against the httpOnly cookie decision. Without that, the rewrite only adds public surface.

## Consequences

- Deploy FastAPI on a private network or internal URL where possible. Admin routes still verify the token on every request (ADR 0003), so this narrows exposure and doesn't replace that check.
- Bringing back a browser-facing `/api` proxy, or a browser Supabase client that calls FastAPI directly, means revisiting this ADR.
