"""Backwards-compatible re-exports for test fakes."""

from pizzeria.infrastructure.repositories.in_memory_pizza_repository import (
    InMemoryPizzaRepository,
)

__all__ = ["InMemoryPizzaRepository"]
