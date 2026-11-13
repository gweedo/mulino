from decimal import Decimal

import pytest

from pizzeria.application.use_cases.reorder_menu import ReorderMenu
from pizzeria.domain.menu_order import InvalidMenuOrder
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza

from .fakes import InMemoryPizzaRepository


def _pizza(name: str) -> Pizza:
    return Pizza.create(name, "", ["x"], set(), Money(Decimal("8"), "EUR"))


async def _menu(*names: str) -> tuple[InMemoryPizzaRepository, list[Pizza]]:
    repo = InMemoryPizzaRepository()
    pizzas = [_pizza(n) for n in names]
    for p in pizzas:
        await repo.add(p)
    return repo, pizzas


async def test_reorder_menu_applies_the_requested_order():
    repo, (a, b, c) = await _menu("A", "B", "C")

    await ReorderMenu(repo).execute([b.id, c.id, a.id])

    assert [p.name for p in await repo.list()] == ["B", "C", "A"]


async def test_reorder_menu_rejects_an_order_that_misses_a_pizza():
    repo, (a, b, c) = await _menu("A", "B", "C")

    with pytest.raises(InvalidMenuOrder):
        await ReorderMenu(repo).execute([c.id, a.id])

    assert [p.name for p in await repo.list()] == ["A", "B", "C"]
