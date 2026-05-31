"""Unit tests for AuthenticateOwner use case."""

from uuid import uuid4

import pytest

from pizzeria.application.errors import InvalidCredentials
from pizzeria.application.use_cases.authenticate_owner import AuthenticateOwner
from pizzeria.domain.owner import Owner
from pizzeria.infrastructure.security.passwords import hash_password, verify_password
from tests.unit.application.fakes import InMemoryOwnerRepository

# Pre-compute once at module level to avoid paying bcrypt/argon2 cost per test.
_PLAIN_PASSWORD = "secret123"
_KNOWN_HASH = hash_password(_PLAIN_PASSWORD)


@pytest.fixture
async def repo() -> InMemoryOwnerRepository:
    r = InMemoryOwnerRepository()
    await r.add(Owner(id=uuid4(), email="owner@example.com", password_hash=_KNOWN_HASH))
    return r


def _stub_encode(sub: str) -> str:
    return f"tok:{sub}"


async def test_valid_credentials_returns_token(repo: InMemoryOwnerRepository):
    uc = AuthenticateOwner(repo, verify_password, _stub_encode)
    token = await uc.execute("owner@example.com", _PLAIN_PASSWORD)
    assert isinstance(token, str)
    assert len(token) > 0


async def test_wrong_password_raises_InvalidCredentials(repo: InMemoryOwnerRepository):
    uc = AuthenticateOwner(repo, verify_password, _stub_encode)
    with pytest.raises(InvalidCredentials):
        await uc.execute("owner@example.com", "wrong-password")


async def test_unknown_email_raises_InvalidCredentials(repo: InMemoryOwnerRepository):
    uc = AuthenticateOwner(repo, verify_password, _stub_encode)
    with pytest.raises(InvalidCredentials):
        await uc.execute("nobody@example.com", _PLAIN_PASSWORD)


async def test_no_info_leak(repo: InMemoryOwnerRepository):
    uc = AuthenticateOwner(repo, verify_password, _stub_encode)
    try:
        await uc.execute("owner@example.com", "wrong-password")
    except InvalidCredentials:
        wrong_password_error = InvalidCredentials

    try:
        await uc.execute("nobody@example.com", _PLAIN_PASSWORD)
    except InvalidCredentials:
        unknown_email_error = InvalidCredentials

    assert wrong_password_error is unknown_email_error


async def test_token_subject_is_owner_email(repo: InMemoryOwnerRepository):
    captured: list[str] = []

    def capture_encode(sub: str) -> str:
        captured.append(sub)
        return "tok"

    uc = AuthenticateOwner(repo, verify_password, capture_encode)
    await uc.execute("owner@example.com", _PLAIN_PASSWORD)
    assert captured == ["owner@example.com"]
