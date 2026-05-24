"""Backwards-compatible re-export.

InMemoryPizzaRepository was promoted to first-class infrastructure in step 07
(see src/pizzeria/infrastructure/repositories/in_memory_pizza_repository.py).
The existing use-case tests still import from this path.
"""

from pizzeria.infrastructure.repositories.in_memory_pizza_repository import (
    InMemoryPizzaRepository,
)

__all__ = ["InMemoryPizzaRepository"]
