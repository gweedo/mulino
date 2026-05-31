from decimal import Decimal
from uuid import UUID

from pizzeria.application.errors import PizzaNotFound
from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money


class UpdatePizza:
    """Use case: update an existing pizza."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(
        self,
        pizza_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        ingredients: list[str] | None = None,
        allergen_names: list[str] | None = None,
        price_amount: Decimal | None = None,
        price_currency: str | None = None,
        available: bool | None = None,
    ) -> None:
        """Execute the update pizza use case."""
        pizza = await self.repository.get(pizza_id)
        if pizza is None:
            raise PizzaNotFound(f"Pizza with id {pizza_id} not found")

        # Orchestrate intent methods on the aggregate
        if name is not None:
            pizza.rename(name)
        if description is not None:
            pizza.change_description(description)
        if ingredients is not None:
            pizza.change_ingredients(ingredients)
        if allergen_names is not None:
            allergens = {Allergen(a) for a in allergen_names}
            pizza.change_allergens(allergens)
        if price_amount is not None and price_currency is not None:
            price = Money(amount=price_amount, currency=price_currency)
            pizza.change_price(price)
        if available is True:
            pizza.mark_available()
        elif available is False:
            pizza.mark_unavailable()

        await self.repository.update(pizza)
