from typing import Protocol
from uuid import UUID

from pizzeria.domain.pizza import Pizza


class PizzaRepository(Protocol):
    """Abstract repository for Pizza aggregate operations."""

    async def add(self, pizza: Pizza) -> None:
        """Add a new pizza to the repository."""
        ...

    async def get(self, pizza_id: UUID) -> Pizza | None:
        """Get a pizza by ID, or None if not found."""
        ...

    async def list(self, *, only_available: bool = False) -> list[Pizza]:
        """List all pizzas, optionally filtering for available only."""
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
