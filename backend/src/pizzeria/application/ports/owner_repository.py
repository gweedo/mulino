from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pizzeria.domain.owner import Owner


class OwnerRepository(Protocol):
    """Abstract repository for Owner aggregate operations.

    The Owner domain type lands in step 08; until then the TYPE_CHECKING
    import is a forward reference. The Protocol itself is import-safe today.
    """

    async def get_by_email(self, email: str) -> Owner | None:
        """Find an owner by email, or None if not found."""
        ...
