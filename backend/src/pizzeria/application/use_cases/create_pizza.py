from pizzeria.application.errors import DuplicatePizzaName
from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza


class CreatePizza:
    """Use case: create a new pizza."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(
        self,
        name: str,
        description: str,
        ingredients: list[str],
        allergens: set[Allergen] | frozenset[Allergen],
        price: Money,
    ) -> Pizza:
        """Execute the create pizza use case."""
        # Check if pizza with same name already exists
        existing = await self.repository.find_by_name(name)
        if existing is not None:
            raise DuplicatePizzaName(f"Pizza with name '{name}' already exists")

        # Create and persist the pizza
        pizza = Pizza.create(name, description, ingredients, allergens, price)
        await self.repository.add(pizza)
        return pizza
