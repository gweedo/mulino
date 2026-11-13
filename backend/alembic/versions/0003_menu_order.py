"""add pizzas.position for the Menu Order

Existing pizzas keep the order they were created in (ties broken by name).
New pizzas draw their position from a sequence, so they always land last.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-10

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = '0003'
down_revision: str | Sequence[str] | None = '0002'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE SEQUENCE pizzeria.pizza_position_seq')
    op.add_column(
        'pizzas',
        sa.Column(
            'position',
            sa.BigInteger(),
            server_default=sa.text("nextval('pizzeria.pizza_position_seq'::regclass)"),
            nullable=False,
        ),
        schema='pizzeria',
    )
    # add_column filled existing rows in physical order; make it deterministic.
    op.execute(
        """
        UPDATE pizzeria.pizzas AS p
        SET position = o.rn
        FROM (
            SELECT id, row_number() OVER (ORDER BY created_at, name) AS rn
            FROM pizzeria.pizzas
        ) AS o
        WHERE p.id = o.id
        """
    )
    op.execute(
        "SELECT setval('pizzeria.pizza_position_seq', "
        "COALESCE((SELECT max(position) FROM pizzeria.pizzas), 0) + 1, false)"
    )
    op.execute('ALTER SEQUENCE pizzeria.pizza_position_seq OWNED BY pizzeria.pizzas.position')


def downgrade() -> None:
    # Dropping the column also drops the sequence it owns.
    op.drop_column('pizzas', 'position', schema='pizzeria')
