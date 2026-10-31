"""API integration test fixtures."""

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from cryptography.hazmat.primitives.asymmetric import ec
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.api.deps import get_key_source, get_session
from pizzeria.api.main import create_app
from tests._auth import make_key, sign_token


@pytest.fixture
def signing_key() -> ec.EllipticCurvePrivateKey:
    """Stands in for the Supabase project's signing key; the app trusts its public half."""
    return make_key()


@pytest_asyncio.fixture
async def app(session: AsyncSession, signing_key: ec.EllipticCurvePrivateKey):
    _app = create_app()

    async def _override() -> AsyncIterator[AsyncSession]:
        yield session

    _app.dependency_overrides[get_session] = _override
    _app.dependency_overrides[get_key_source] = lambda: lambda _token: signing_key.public_key()
    yield _app
    _app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as c:
        yield c


@pytest.fixture
def auth_headers(signing_key: ec.EllipticCurvePrivateKey) -> dict[str, str]:
    """Bearer header for a signed-in Menu Manager."""
    return {"Authorization": f"Bearer {sign_token(signing_key)}"}
