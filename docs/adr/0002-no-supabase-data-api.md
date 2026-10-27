# No Supabase Data API; app tables in a private schema

FastAPI is the only way into the data, so Supabase's auto-generated Data API (REST and GraphQL) is switched off on every project, and app tables live in a private `pizzeria` schema that is never added to Supabase's exposed schemas. Supabase exposes `public` by default, and a table there without Row Level Security is readable and writable by anyone holding the public key.

## Considered Options

- **RLS with no policies on `public.pizzas`** — rejected in favour of keeping app tables off the exposed surface entirely.

## Consequences

Switching the Data API off is a dashboard setting, so it is a project-setup step in the runbook. Re-enabling the Data API or exposing `pizzeria` would bypass every domain rule — revisit this ADR before doing either.
