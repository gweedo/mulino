"""API integration test fixtures."""

from collections.abc import AsyncIterator
from uuid import uuid4

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.api.deps import get_session
from pizzeria.api.limiter import limiter
from pizzeria.api.main import create_app
from pizzeria.infrastructure.models import OwnerORM
from pizzeria.infrastructure.security.passwords import hash_password


@pytest_asyncio.fixture
async def app(session: AsyncSession):
    limiter._storage.reset()  # isolate rate-limit counters between tests
    _app = create_app()

    async def _override() -> AsyncIterator[AsyncSession]:
        yield session

    _app.dependency_overrides[get_session] = _override
    yield _app
    _app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:
        yield c


@pytest_asyncio.fixture
async def test_owner(session: AsyncSession) -> dict:
    plain_password = "secret123"
    owner = OwnerORM(
        id=uuid4(),
        email="owner@pizzeria.test",
        password_hash=hash_password(plain_password),
    )
    session.add(owner)
    await session.flush()
    return {"id": owner.id, "email": owner.email, "password": plain_password}


@pytest_asyncio.fixture
async def auth_cookie(client: AsyncClient, test_owner: dict) -> str:
    resp = await client.post(
        "/api/auth/login",
        json={"email": test_owner["email"], "password": test_owner["password"]},
    )
    assert resp.status_code == 200
    cookie = resp.cookies.get("session")
    assert cookie is not None
    return cookie
