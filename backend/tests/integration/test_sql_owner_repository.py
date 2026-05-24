"""SqlOwnerRepository integration tests (real Postgres)."""

from uuid import uuid4

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.infrastructure.models import OwnerORM
from pizzeria.infrastructure.repositories.owner_repository import SqlOwnerRepository


@pytest_asyncio.fixture
async def repo(session: AsyncSession) -> SqlOwnerRepository:
    return SqlOwnerRepository(session)


async def test_get_by_email_returns_owner_when_present(
    repo: SqlOwnerRepository, session: AsyncSession
):
    oid = uuid4()
    session.add(OwnerORM(id=oid, email="owner@example.com", password_hash="bcrypt$hash"))
    await session.flush()

    fetched = await repo.get_by_email("owner@example.com")
    assert fetched is not None
    assert fetched.id == oid
    assert fetched.email == "owner@example.com"
    assert fetched.password_hash == "bcrypt$hash"


async def test_get_by_email_returns_none_when_missing(repo: SqlOwnerRepository):
    assert await repo.get_by_email("nobody@example.com") is None


async def test_get_by_email_is_case_sensitive(
    repo: SqlOwnerRepository, session: AsyncSession
):
    session.add(OwnerORM(id=uuid4(), email="Owner@Example.com", password_hash="h"))
    await session.flush()
    assert await repo.get_by_email("owner@example.com") is None
    assert await repo.get_by_email("Owner@Example.com") is not None
