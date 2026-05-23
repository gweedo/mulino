from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.pizza import Pizza


class ListPizzas:
    """Use case: list all pizzas, optionally filtering for available only."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(self, *, only_available: bool = False) -> list[Pizza]:
        """Execute the list pizzas use case."""
        return await self.repository.list(only_available=only_available)
