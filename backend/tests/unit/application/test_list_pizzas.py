from decimal import Decimal

import pytest

from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza
from pizzeria.application.use_cases.list_pizzas import ListPizzas
from .fakes import InMemoryPizzaRepository


@pytest.fixture
async def repo():
    return InMemoryPizzaRepository()


@pytest.mark.asyncio
async def test_list_pizzas_empty():
    """ListPizzas returns empty list when no pizzas exist."""
    repo = InMemoryPizzaRepository()
    use_case = ListPizzas(repo)
    result = await use_case.execute()
    assert result == []


@pytest.mark.asyncio
async def test_list_pizzas_all():
    """ListPizzas returns all pizzas."""
    repo = InMemoryPizzaRepository()
    p1 = Pizza.create("Pizza 1", "", ["x"], set(), Money(Decimal("10"), "EUR"))
    p2 = Pizza.create("Pizza 2", "", ["x"], set(), Money(Decimal("20"), "EUR"))
    await repo.add(p1)
    await repo.add(p2)

    use_case = ListPizzas(repo)
    result = await use_case.execute()
    assert len(result) == 2
    assert p1 in result
    assert p2 in result


@pytest.mark.asyncio
async def test_list_pizzas_only_available():
    """ListPizzas with only_available=True returns only available pizzas."""
    repo = InMemoryPizzaRepository()
    p1 = Pizza.create("Pizza 1", "", ["x"], set(), Money(Decimal("10"), "EUR"))
    p2 = Pizza.create("Pizza 2", "", ["x"], set(), Money(Decimal("20"), "EUR"))
    p1.mark_unavailable()
    await repo.add(p1)
    await repo.add(p2)

    use_case = ListPizzas(repo)
    result = await use_case.execute(only_available=True)
    assert len(result) == 1
    assert p2 in result
    assert p1 not in result
