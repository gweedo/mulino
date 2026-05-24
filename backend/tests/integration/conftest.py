"""Integration test fixtures: real Postgres with per-test SAVEPOINT isolation.

Bootstrap runs in TWO phases to avoid a nested-event-loop conflict:

  1. `_bootstrap_test_db` (sync, session-scoped) — auto-creates the target DB
     if missing, then runs `alembic upgrade head` once. Both internally use
     asyncio.run(...), which requires no event loop to be running yet — hence
     sync, not pytest-asyncio.

  2. `engine` / `connection` / `session` (async) — open the async engine,
     then for each test wrap a connection in an outer rollback plus a SAVEPOINT.
     Teardown rolls back the SAVEPOINT and the outer transaction, leaving the
     DB identical to its post-migration state.

CI's service container ships pizzeria_test pre-created, so the create-if-missing
path becomes a no-op there.
"""

import asyncio
from collections.abc import AsyncIterator
from urllib.parse import urlparse, urlunparse

import asyncpg
import pytest
import pytest_asyncio
from alembic.config import Config
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from alembic import command
from pizzeria.infrastructure.settings import get_settings


def _alembic_config(database_url: str) -> Config:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", database_url)
    return cfg


async def _create_db_if_missing(database_url: str) -> None:
    parsed = urlparse(database_url)
    target_db = parsed.path.lstrip("/")
    if not target_db:
        return
    admin_url = urlunparse(parsed._replace(path="/postgres"))
    admin_dsn = admin_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(admin_dsn)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", target_db
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{target_db}"')
    finally:
        await conn.close()


@pytest.fixture(scope="session")
def _bootstrap_test_db() -> str:
    """Sync session-scoped bootstrap. Returns the resolved DATABASE_URL."""
    url = get_settings().DATABASE_URL
    asyncio.run(_create_db_if_missing(url))
    command.upgrade(_alembic_config(url), "head")
    return url


@pytest_asyncio.fixture(scope="session")
async def engine(_bootstrap_test_db: str) -> AsyncIterator[AsyncEngine]:
    eng = create_async_engine(_bootstrap_test_db, future=True)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def connection(engine: AsyncEngine) -> AsyncIterator[AsyncConnection]:
    """Outer transaction rolled back at teardown — wraps the SAVEPOINT below."""
    async with engine.connect() as conn:
        outer = await conn.begin()
        try:
            yield conn
        finally:
            await outer.rollback()


@pytest_asyncio.fixture
async def session(connection: AsyncConnection) -> AsyncIterator[AsyncSession]:
    """AsyncSession that runs inside a SAVEPOINT on the rollback-protected connection.

    `join_transaction_mode="create_savepoint"` (SQLAlchemy 2.0+) makes the session
    automatically open a SAVEPOINT on join and re-open it after every flush/commit,
    so test code can freely call session.commit() without persisting beyond the
    test.
    """
    async with AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    ) as s:
        yield s
