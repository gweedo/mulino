from uuid import UUID

from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.application.errors import PizzaNotFound


class UpdatePizza:
    """Use case: update an existing pizza."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(
        self,
        pizza_id: UUID,
        name: str | None = None,
        description: str | None = None,
        ingredients: list[str] | None = None,
        allergens: set[Allergen] | frozenset[Allergen] | None = None,
        price: Money | None = None,
    ) -> None:
        """Execute the update pizza use case."""
        pizza = await self.repository.get(pizza_id)
        if pizza is None:
            raise PizzaNotFound(f"Pizza with id {pizza_id} not found")

        pizza.update(name, description, ingredients, allergens, price)
        await self.repository.update(pizza)
