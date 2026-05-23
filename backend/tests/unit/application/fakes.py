from uuid import UUID

from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.pizza import Pizza


class InMemoryPizzaRepository(PizzaRepository):
    """In-memory implementation of PizzaRepository for testing."""

    def __init__(self):
        self._pizzas: dict[UUID, Pizza] = {}

    async def add(self, pizza: Pizza) -> None:
        self._pizzas[pizza.id] = pizza

    async def get(self, pizza_id: UUID) -> Pizza | None:
        return self._pizzas.get(pizza_id)

    async def list(self, *, only_available: bool = False) -> list[Pizza]:
        pizzas = list(self._pizzas.values())
        if only_available:
            return [p for p in pizzas if p.available]
        return pizzas

    async def update(self, pizza: Pizza) -> None:
        self._pizzas[pizza.id] = pizza

    async def delete(self, pizza_id: UUID) -> None:
        self._pizzas.pop(pizza_id, None)

    async def find_by_name(self, name: str) -> Pizza | None:
        for pizza in self._pizzas.values():
            if pizza.name == name:
                return pizza
        return None
