from uuid import UUID

from pizzeria.application.errors import PizzaNotFound
from pizzeria.application.ports.pizza_repository import PizzaRepository


class DeletePizza:
    """Use case: delete a pizza by ID."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(self, pizza_id: UUID) -> None:
        """Execute the delete pizza use case."""
        pizza = await self.repository.get(pizza_id)
        if pizza is None:
            raise PizzaNotFound(f"Pizza with id {pizza_id} not found")

        await self.repository.delete(pizza_id)
