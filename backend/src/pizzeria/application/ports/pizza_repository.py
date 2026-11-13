from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from pizzeria.domain.pizza import Pizza


class PizzaRepository(Protocol):
    """Abstract repository for Pizza aggregate operations."""

    async def add(self, pizza: Pizza) -> None:
        """Add a new pizza at the end of the Menu Order."""
        ...

    async def get(self, pizza_id: UUID) -> Pizza | None:
        """Get a pizza by ID, or None if not found."""
        ...

    async def list(self, *, only_available: bool = False) -> list[Pizza]:
        """List pizzas in Menu Order, optionally filtering for available only."""
        ...

    async def reorder(self, pizza_ids: Sequence[UUID]) -> None:
        """Store a new Menu Order. `pizza_ids` must list every pizza exactly once
        (callers validate it with MenuOrder.rearrange)."""
        ...

    async def update(self, pizza: Pizza) -> None:
        """Update an existing pizza."""
        ...

    async def delete(self, pizza_id: UUID) -> None:
        """Delete a pizza by ID."""
        ...

    async def find_by_name(self, name: str) -> Pizza | None:
        """Find a pizza by name, or None if not found."""
        ...
