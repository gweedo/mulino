from decimal import Decimal
from uuid import uuid4

import pytest

from pizzeria.application.errors import PizzaNotFound
from pizzeria.application.use_cases.delete_pizza import DeletePizza
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza

from .fakes import InMemoryPizzaRepository


@pytest.mark.asyncio
async def test_delete_pizza_success():
    """DeletePizza removes pizza from repository."""
    repo = InMemoryPizzaRepository()
    p = Pizza.create("Pizza", "", ["x"], set(), Money(Decimal("10"), "EUR"))
    await repo.add(p)

    use_case = DeletePizza(repo)
    await use_case.execute(p.id)

    assert await repo.get(p.id) is None


@pytest.mark.asyncio
async def test_delete_pizza_not_found():
    """DeletePizza raises PizzaNotFound if pizza doesn't exist."""
    repo = InMemoryPizzaRepository()
    use_case = DeletePizza(repo)

    with pytest.raises(PizzaNotFound):
        await use_case.execute(uuid4())
