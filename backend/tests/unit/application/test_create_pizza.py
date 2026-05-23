from decimal import Decimal

import pytest

from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.application.use_cases.create_pizza import CreatePizza
from pizzeria.application.errors import DuplicatePizzaName
from .fakes import InMemoryPizzaRepository


@pytest.mark.asyncio
async def test_create_pizza_success():
    """CreatePizza creates and returns new pizza."""
    repo = InMemoryPizzaRepository()
    use_case = CreatePizza(repo)

    pizza = await use_case.execute(
        name="Margherita",
        description="Classic",
        ingredients=["tomato", "mozzarella"],
        allergens={Allergen.milk},
        price=Money(Decimal("10.00"), "EUR"),
    )

    assert pizza.name == "Margherita"
    assert pizza.description == "Classic"
    assert pizza.ingredients == ["tomato", "mozzarella"]
    assert Allergen.milk in pizza.allergens
    assert pizza.price == Money(Decimal("10.00"), "EUR")

    # Verify it was persisted
    retrieved = await repo.get(pizza.id)
    assert retrieved == pizza


@pytest.mark.asyncio
async def test_create_pizza_duplicate_name():
    """CreatePizza raises DuplicatePizzaName if name already exists."""
    repo = InMemoryPizzaRepository()
    use_case = CreatePizza(repo)

    await use_case.execute(
        name="Margherita",
        description="",
        ingredients=["x"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )

    with pytest.raises(DuplicatePizzaName):
        await use_case.execute(
            name="Margherita",
            description="",
            ingredients=["y"],
            allergens=set(),
            price=Money(Decimal("15"), "EUR"),
        )
