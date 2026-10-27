from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from pizzeria.domain.menu_manager import MenuManager


def test_menu_manager_creation():
    """MenuManager is created with the Supabase user id and email."""
    mid = uuid4()
    m = MenuManager(id=mid, email="owner@example.com")
    assert m.id == mid
    assert m.email == "owner@example.com"


def test_menu_manager_is_frozen():
    """MenuManager is immutable — attribute assignment raises FrozenInstanceError."""
    m = MenuManager(id=uuid4(), email="owner@example.com")
    with pytest.raises(FrozenInstanceError):
        m.email = "other@example.com"  # type: ignore[misc]


def test_menu_manager_equality():
    """Two MenuManager objects with same fields are equal."""
    mid = uuid4()
    assert MenuManager(id=mid, email="a@example.com") == MenuManager(id=mid, email="a@example.com")


def test_menu_manager_email_must_be_non_empty():
    """Empty email is rejected."""
    with pytest.raises(ValueError, match="email must be non-empty"):
        MenuManager(id=uuid4(), email="")


def test_menu_manager_email_must_contain_at_sign():
    """Email without '@' is rejected (basic shape check)."""
    with pytest.raises(ValueError, match="email must contain '@'"):
        MenuManager(id=uuid4(), email="not-an-email")
