from decimal import Decimal

import pytest

from pizzeria.application.errors import PizzaNotFound
from pizzeria.application.use_cases.get_pizza import GetPizza
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza

from .fakes import InMemoryPizzaRepository


@pytest.mark.asyncio
async def test_get_pizza_found():
    """GetPizza returns pizza when found by ID."""
    repo = InMemoryPizzaRepository()
    p = Pizza.create("Pizza", "", ["x"], set(), Money(Decimal("10"), "EUR"))
    await repo.add(p)

    use_case = GetPizza(repo)
    result = await use_case.execute(p.id)
    assert result == p


@pytest.mark.asyncio
async def test_get_pizza_not_found():
    """GetPizza raises PizzaNotFound when pizza ID doesn't exist."""
    from uuid import uuid4

    repo = InMemoryPizzaRepository()
    use_case = GetPizza(repo)

    with pytest.raises(PizzaNotFound):
        await use_case.execute(uuid4())
