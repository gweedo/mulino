# Supabase setup

[← Back to docs index](./README.md)

How to set up a Supabase project for Mulino from scratch, all the way to a working
login. Do it once per environment: a `mulino-dev` project for local development
and a separate `mulino-prod` project for production. Never share users between them.

Supabase provides two things here: the managed Postgres and Auth (login). FastAPI
remains the only way into the data. See [ADR 0001](./adr/0001-supabase-for-database-and-auth.md),
[ADR 0002](./adr/0002-no-supabase-data-api.md) and [ADR 0003](./adr/0003-menu-manager-role-claim.md).

> Supabase moves dashboard menus around now and then. If a label doesn't match
> exactly, look for the nearest equivalent.

## 1. Create the project

1. Sign up at <https://supabase.com> and create an organization (the free plan is fine).
2. Click **New project** and fill in:
   - **Name**, for example `mulino-dev`.
   - **Database password**: generate a strong one and save it in a password
     manager. Supabase won't show it again, and you need it for the connection string.
   - **Region**: the one closest to your users, for example Frankfurt (`eu-central-1`).
3. Wait for the project to finish setting up.
4. Copy the **project ref** from the URL (`https://supabase.com/dashboard/project/<ref>`).
   Your `SUPABASE_URL` is `https://<ref>.supabase.co`.

## 2. Asymmetric JWT signing keys

FastAPI accepts only ES256/RS256 tokens, verified against the project's public keys
(JWKS). It rejects the legacy HS256 shared secret.

1. Go to **Project Settings → JWT Keys** (or **Authentication → JWT Signing Keys**).
2. If the current key is **ECC (P-256)**, you're done. Newer projects often start this way.
3. If it is **Legacy HS256 (shared secret)**: click **Migrate JWT secret**, then
   **Rotate keys** so the ECC key becomes current.
4. Check:
   ```bash
   curl https://<ref>.supabase.co/auth/v1/.well-known/jwks.json
   ```
   The response must contain a key with `"alg":"ES256"`. An empty `keys` array means
   the rotation didn't happen.

## 3. API keys

**Project Settings → API Keys** shows two kinds of key:

- **Publishable key** (`sb_publishable_…`): copy it into `frontend/.env.local` as
  `SUPABASE_PUBLISHABLE_KEY`.
- **Secret keys** (`sb_secret_…`): never copy these anywhere. They bypass every
  protection, and the app doesn't need them.

Ignore the **Legacy API keys** tab (`anon`, `service_role`).

## 4. Turn off the Data API

1. Go to **Project Settings → Data API** (or **Integrations → Data API**).
2. Switch **Enable Data API** off and save. Never add `pizzeria` to the exposed schemas.
3. Check:
   ```bash
   curl -i https://<ref>.supabase.co/rest/v1/ -H "apikey: <publishable key>"
   ```
   This must return an error, not a list of tables. Login (`/auth/v1`) keeps working.

## 5. Lock down sign-in

1. **Authentication → Sign In / Providers**:
   - Turn **Allow new users to sign up** off. Users are created only from the dashboard.
   - Leave the **Email** provider enabled.
2. *Optional:* in the same page, click **Email** and set **Minimum password length**
   to 12 or more. If the field isn't there, try **Authentication → Attack Protection**.
   Don't confuse this with **Authentication → Policies**: that page holds Row Level
   Security rules for tables, which we don't use, so leave it alone.
3. *Optional, needed later for password recovery:* in **Authentication → URL Configuration**,
   set **Site URL** to `http://localhost:3000` (dev) or the production URL.

## 6. Create the Menu Manager

1. **Authentication → Users → Add user → Create new user**: enter an email and a password,
   tick **Auto Confirm User**, then click **Create user**.
2. Grant the role. There's no table to create: `auth.users` already exists, and this only
   edits the user's row. Open **SQL Editor → + New query**, then run:
   ```sql
   UPDATE auth.users
   SET raw_app_meta_data = raw_app_meta_data || '{"role": "menu_manager"}'
   WHERE email = 'you@example.com';
   ```
   - If the editor warns about a potentially destructive query, confirm. The `WHERE`
     clause limits it to one user.
   - "Success. No rows returned" is the expected result.
3. Check:
   ```sql
   SELECT email, raw_app_meta_data FROM auth.users;
   ```
   The row must contain `"role": "menu_manager"`. The role appears in tokens issued
   from the **next** sign-in.
4. *Optional:* create a second user **without** the role (repeat step 1 only) to test
   that the admin area answers 403.

## 7. Database and migrations

Choose where the pizza data lives:

- **Local Postgres:** keep `DATABASE_URL` on the devcontainer database. Supabase is then
  used for login only. Run `uv run alembic upgrade head` as usual.
- **Supabase Postgres:** follow the steps below.

### Find the connection string

1. Click **Connect** at the top of the project page.
2. On the **Connection String** tab, choose **Session pooler**. It may be a dropdown,
   a section further down, or behind the "Not IPv4 compatible" note on the direct
   connection.
3. The string looks like this:
   ```
   postgresql://postgres.<ref>:[YOUR-PASSWORD]@aws-<n>-<region>.pooler.supabase.com:5432/postgres
   ```
   - The user is `postgres.<ref>` and the port is **5432**.
   - Copy the host exactly; the `aws-<n>` part varies between projects.
4. Edit it:
   - Change `postgresql://` to `postgresql+asyncpg://`.
   - Replace `[YOUR-PASSWORD]`, URL-encoding special characters: `@` → `%40`,
     `#` → `%23`, `/` → `%2F`, `:` → `%3A`.

### Which connection to use

| Connection | Port | Use |
|---|---|---|
| Direct (`db.<ref>.supabase.co`) | 5432 | Migrations in production. IPv6-only unless you buy the IPv4 add-on. |
| **Session pooler** | 5432 | The app, and migrations from IPv4-only machines (WSL, devcontainers). |
| Transaction pooler | 6543 | **Never.** asyncpg needs prepared statements. |

### Run the migrations

Use `export` in the terminal. Don't use `backend/.env`: the devcontainer sets its own
`DATABASE_URL`, and that value wins over `.env`. Keep the single quotes, and type the
commands rather than pasting them. A pasted invisible character makes Alembic fail
with `unrecognized arguments:`.

```bash
cd backend
export DATABASE_URL='postgresql+asyncpg://postgres.<ref>:<encoded-password>@aws-<n>-<region>.pooler.supabase.com:5432/postgres'
uv run alembic upgrade head
uv run python -m pizzeria.seed_pizzas   # optional: 7 sample pizzas
```

The migration creates the private `pizzeria` schema and revokes Supabase's `anon` and
`authenticated` roles from it. In **Table Editor**, pick the schema **`pizzeria`**
(top left) to see the tables. `public` stays empty.

## 8. Environment files

`backend/.env`:
```
SUPABASE_URL=https://<ref>.supabase.co
```

`frontend/.env.local` (template: `frontend/.env.example`):
```
BACKEND_INTERNAL_URL=http://localhost:8000
SUPABASE_URL=https://<ref>.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
```

Don't use quotes or spaces around `=`. Never prefix these with `NEXT_PUBLIC_`: they
are read by the Next.js server only.

## 9. Run

Terminal 1, backend:
```bash
cd backend
export DATABASE_URL='<same session-pooler URL>'   # skip it to use local Postgres
uv run uvicorn pizzeria.api.main:app --reload
```

Terminal 2, frontend (restart it after editing `.env.local`):
```bash
cd frontend
npm install
npm run dev
```

Run the backend tests in a third terminal **without** the export. They use the local
`pizzeria_test` database and never talk to Supabase.

## 10. Verify

1. <http://localhost:3000> shows the menu.
2. `/admin` redirects to the login page.
3. Log in as the Menu Manager. The admin page shows the pizza list.
4. In DevTools → **Application → Cookies → localhost:3000**, the cookie
   `sb-<ref>-auth-token` has **HttpOnly** ticked.
5. Create, edit, hide and delete a pizza; the homepage updates.
6. Log out; `/admin` redirects again.
7. The user without the role is refused (403).
8. The `curl` from step 4 still returns an error.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| Login says wrong credentials | Wrong email or password, or the user wasn't auto-confirmed (Authentication → Users). |
| Logged in, but admin says "Invalid session" | Signing keys are still HS256. Repeat step 2. |
| Admin says "Not a menu manager" | The role is missing. Run the check in step 6.3, then log out and back in. |
| Backend fails at startup about `SUPABASE_URL` | Missing from `backend/.env`. Restart uvicorn after adding it. |
| Menu is empty or shows old pizzas | The `export DATABASE_URL` didn't happen in the backend terminal. |
| `alembic: error: unrecognized arguments:` | The command was pasted with an invisible character, or the URL isn't in single quotes. |

## Operations

- **Free projects pause** after about 7 days without activity. Click **Restore** in
  the dashboard.
- **Auth rate limits** are under Authentication → Rate Limits. The login action adds
  its own limit of 5 attempts per minute per IP.
- **Lost password** (until in-app recovery ships): delete the user in
  Authentication → Users, recreate it (step 6), and grant the role again.
- **Production deploy:** run `alembic upgrade head` over the direct connection (or the
  session pooler) **before** starting uvicorn on the session pooler. See
  [Development](./development.md).
