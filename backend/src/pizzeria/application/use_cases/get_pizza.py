from uuid import UUID

from pizzeria.domain.pizza import Pizza
from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.application.errors import PizzaNotFound


class GetPizza:
    """Use case: get a pizza by ID."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(self, pizza_id: UUID) -> Pizza:
        """Execute the get pizza use case."""
        pizza = await self.repository.get(pizza_id)
        if pizza is None:
            raise PizzaNotFound(f"Pizza with id {pizza_id} not found")
        return pizza
