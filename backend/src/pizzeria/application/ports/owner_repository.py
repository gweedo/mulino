from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pizzeria.domain.owner import Owner


class OwnerRepository(Protocol):
    """Abstract repository for Owner aggregate operations."""

    async def get_by_email(self, email: str) -> Owner | None:
        """Find an owner by email, or None if not found."""
        ...
