# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

This repo is **single-context**. Its glossary is **`CONTEXT.md`** at the repo root (it plays the role the skills call `GLOSSARY.md`). Do not create a separate `GLOSSARY.md`; add or sharpen terms in `CONTEXT.md`.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root: the domain glossary (Menu, Menu Manager, Pizza, …).
- **`docs/adr/`**: read ADRs that touch the area you're about to work in.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill (reached via `/grill-with-docs` and `/improve-codebase-architecture`) updates them when terms or decisions actually get resolved.

## File structure

```
/
├── CONTEXT.md          ← glossary
├── docs/adr/
│   ├── 0001-supabase-for-database-and-auth.md
│   ├── 0002-no-supabase-data-api.md
│   └── 0003-menu-manager-role-claim.md
├── backend/
└── frontend/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids (e.g. say "Menu Manager", not "owner" or "admin").

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0002 (no Supabase Data API), but worth reopening because…_
