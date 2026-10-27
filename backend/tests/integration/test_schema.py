"""The migrated schema keeps app tables in the private `pizzeria` schema (ADR 0002)."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def _schemas_of(session: AsyncSession, table: str) -> list[str]:
    rows = await session.execute(
        text("SELECT table_schema FROM information_schema.tables WHERE table_name = :t"),
        {"t": table},
    )
    return [r[0] for r in rows]


async def test_pizzas_table_lives_in_private_schema(session: AsyncSession) -> None:
    assert await _schemas_of(session, "pizzas") == ["pizzeria"]


async def test_owners_table_is_dropped(session: AsyncSession) -> None:
    assert await _schemas_of(session, "owners") == []
