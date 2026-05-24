from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from pizzeria.domain.owner import Owner


def test_owner_creation():
    """Owner can be created with id, email, and password_hash."""
    oid = uuid4()
    o = Owner(id=oid, email="owner@example.com", password_hash="bcrypt$hash")
    assert o.id == oid
    assert o.email == "owner@example.com"
    assert o.password_hash == "bcrypt$hash"


def test_owner_is_frozen():
    """Owner is immutable — attribute assignment raises FrozenInstanceError."""
    o = Owner(id=uuid4(), email="owner@example.com", password_hash="hash")
    with pytest.raises(FrozenInstanceError):
        o.email = "other@example.com"  # type: ignore[misc]


def test_owner_equality():
    """Two Owner objects with same fields are equal."""
    oid = uuid4()
    o1 = Owner(id=oid, email="owner@example.com", password_hash="hash")
    o2 = Owner(id=oid, email="owner@example.com", password_hash="hash")
    assert o1 == o2


def test_owner_inequality():
    """Owner objects with different fields are not equal."""
    o1 = Owner(id=uuid4(), email="owner@example.com", password_hash="hash")
    o2 = Owner(id=uuid4(), email="owner@example.com", password_hash="hash")
    assert o1 != o2


def test_owner_email_must_be_non_empty():
    """Empty email is rejected."""
    with pytest.raises(ValueError, match="email must be non-empty"):
        Owner(id=uuid4(), email="", password_hash="hash")


def test_owner_email_must_contain_at_sign():
    """Email without '@' is rejected (basic shape check; full RFC 5322 is API-layer)."""
    with pytest.raises(ValueError, match="email must contain '@'"):
        Owner(id=uuid4(), email="not-an-email", password_hash="hash")


def test_owner_password_hash_must_be_non_empty():
    """Empty password_hash is rejected — guards against accidental unhashed storage."""
    with pytest.raises(ValueError, match="password_hash must be non-empty"):
        Owner(id=uuid4(), email="owner@example.com", password_hash="")
