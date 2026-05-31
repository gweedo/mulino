from uuid import UUID

from pizzeria.application.errors import PizzaNotFound
from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.pizza import Pizza


class GetPizza:
    """Use case: get a pizza by ID."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(self, pizza_id: UUID, *, only_available: bool = False) -> Pizza:
        """Execute the get pizza use case."""
        pizza = await self.repository.get(pizza_id)
        if pizza is None or (only_available and not pizza.available):
            raise PizzaNotFound(f"Pizza with id {pizza_id} not found")
        return pizza
