"""move app tables to private pizzeria schema; drop owners

Login moved to Supabase Auth (ADR 0001), so the owners table is gone. App tables
live in a schema Supabase's Data API never exposes (ADR 0002).

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-27

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '0002'
down_revision: str | Sequence[str] | None = '0001'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Supabase's public roles only exist on Supabase; plain Postgres (devcontainer, CI)
# skips the revoke.
_REVOKE_PUBLIC_ROLES = """
DO $$
DECLARE r text;
BEGIN
    FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
            EXECUTE format('REVOKE ALL ON SCHEMA pizzeria FROM %I', r);
            EXECUTE format('REVOKE ALL ON ALL TABLES IN SCHEMA pizzeria FROM %I', r);
        END IF;
    END LOOP;
END $$;
"""


def upgrade() -> None:
    op.execute('CREATE SCHEMA IF NOT EXISTS pizzeria')
    op.execute('ALTER TABLE public.pizzas SET SCHEMA pizzeria')
    op.drop_table('owners')
    op.execute(_REVOKE_PUBLIC_ROLES)


def downgrade() -> None:
    op.create_table('owners',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.execute('ALTER TABLE pizzeria.pizzas SET SCHEMA public')
    op.execute('DROP SCHEMA pizzeria')
