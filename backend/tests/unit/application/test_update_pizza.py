from decimal import Decimal
from uuid import uuid4

import pytest

from pizzeria.application.errors import PizzaNotFound
from pizzeria.application.use_cases.update_pizza import UpdatePizza
from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza

from .fakes import InMemoryPizzaRepository


@pytest.mark.asyncio
async def test_update_pizza_success():
    """UpdatePizza updates pizza attributes."""
    repo = InMemoryPizzaRepository()
    p = Pizza.create("Original", "desc", ["x"], set(), Money(Decimal("10"), "EUR"))
    await repo.add(p)

    use_case = UpdatePizza(repo)
    await use_case.execute(
        pizza_id=p.id,
        name="Updated",
        description="new desc",
        ingredients=["y"],
        allergens={Allergen.gluten},
        price=Money(Decimal("15"), "EUR"),
    )

    updated = await repo.get(p.id)
    assert updated.name == "Updated"
    assert updated.description == "new desc"
    assert updated.ingredients == ["y"]
    assert Allergen.gluten in updated.allergens


@pytest.mark.asyncio
async def test_update_pizza_not_found():
    """UpdatePizza raises PizzaNotFound if pizza doesn't exist."""
    repo = InMemoryPizzaRepository()
    use_case = UpdatePizza(repo)

    with pytest.raises(PizzaNotFound):
        await use_case.execute(
            pizza_id=uuid4(),
            name="X",
            description="",
            ingredients=["x"],
            allergens=set(),
            price=Money(Decimal("10"), "EUR"),
        )
