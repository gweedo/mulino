"""Integration tests for pizzeria.seed_owner."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.infrastructure.models import OwnerORM
from pizzeria.infrastructure.security.passwords import hash_password, verify_password
from pizzeria.seed_owner import _main_async, seed_owner


@pytest.mark.asyncio
async def test_creates_owner_when_missing(session: AsyncSession) -> None:
    """Empty owners table → seed creates row and returns 'created'."""
    result = await seed_owner(
        session, email="owner@example.com", password="secret123", force_reset=False
    )
    assert result == "created"

    rows = (
        await session.execute(
            select(OwnerORM).where(OwnerORM.email == "owner@example.com")
        )
    ).scalars().all()
    assert len(rows) == 1
    assert verify_password("secret123", rows[0].password_hash)


@pytest.mark.asyncio
async def test_noop_when_owner_exists_same_email(session: AsyncSession) -> None:
    """Existing owner, no OWNER_FORCE_RESET → returns 'noop', hash unchanged."""
    original_hash = hash_password("original")
    session.add(
        OwnerORM(id=uuid4(), email="owner@example.com", password_hash=original_hash)
    )
    await session.flush()

    result = await seed_owner(
        session, email="owner@example.com", password="different", force_reset=False
    )
    assert result == "noop"

    row = (
        await session.execute(
            select(OwnerORM).where(OwnerORM.email == "owner@example.com")
        )
    ).scalar_one()
    assert row.password_hash == original_hash


@pytest.mark.asyncio
async def test_force_reset_overwrites_password_hash(session: AsyncSession) -> None:
    """OWNER_FORCE_RESET=1 with existing owner → returns 'updated', hash changed."""
    original_hash = hash_password("original")
    session.add(
        OwnerORM(id=uuid4(), email="owner@example.com", password_hash=original_hash)
    )
    await session.flush()

    result = await seed_owner(
        session, email="owner@example.com", password="newsecret", force_reset=True
    )
    assert result == "updated"

    row = (
        await session.execute(
            select(OwnerORM).where(OwnerORM.email == "owner@example.com")
        )
    ).scalar_one()
    assert row.password_hash != original_hash
    assert verify_password("newsecret", row.password_hash)


@pytest.mark.asyncio
async def test_force_reset_when_missing_creates(session: AsyncSession) -> None:
    """OWNER_FORCE_RESET=1 with no existing owner → returns 'created'."""
    result = await seed_owner(
        session, email="owner@example.com", password="secret", force_reset=True
    )
    assert result == "created"


@pytest.mark.asyncio
async def test_main_raises_when_email_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """_main_async raises RuntimeError mentioning OWNER_EMAIL when env var absent."""
    monkeypatch.delenv("OWNER_EMAIL", raising=False)
    monkeypatch.setenv("OWNER_PASSWORD", "somepassword")
    with pytest.raises(RuntimeError, match="OWNER_EMAIL"):
        await _main_async()


@pytest.mark.asyncio
async def test_main_raises_when_password_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """_main_async raises RuntimeError mentioning OWNER_PASSWORD when env var absent."""
    monkeypatch.setenv("OWNER_EMAIL", "owner@example.com")
    monkeypatch.delenv("OWNER_PASSWORD", raising=False)
    with pytest.raises(RuntimeError, match="OWNER_PASSWORD"):
        await _main_async()
