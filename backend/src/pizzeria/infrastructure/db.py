from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from pizzeria.infrastructure.settings import get_settings


def make_engine(database_url: str | None = None) -> AsyncEngine:
    """Create an async SQLAlchemy engine.

    If no URL is supplied, reads DATABASE_URL from the environment via Settings.
    """
    url = database_url or get_settings().DATABASE_URL
    return create_async_engine(url, future=True)


def make_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
