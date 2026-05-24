"""Abstract repository contract: same tests run against every PizzaRepository impl.

Concrete suites (in tests/unit/application/ and tests/integration/) inherit this
class and provide a `repo` fixture yielding their implementation. The day either
implementation drifts from the PizzaRepository Protocol, both suites fail.
"""

from decimal import Decimal
from uuid import uuid4

import pytest

from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza


def _make_pizza(name: str = "Margherita", *, available: bool = True) -> Pizza:
    p = Pizza.create(
        name=name,
        description=f"A delicious {name}",
        ingredients=["tomato", "mozzarella"],
        allergens={Allergen.gluten, Allergen.milk},
        price=Money(amount=Decimal("8.50"), currency="EUR"),
    )
    if not available:
        p.mark_unavailable()
    return p


class PizzaRepositoryContract:
    """Subclass and override the `repo` fixture to test any PizzaRepository impl."""

    @pytest.fixture
    async def repo(self) -> PizzaRepository:
        raise NotImplementedError("Subclasses must override the `repo` fixture")

    async def test_add_then_get_roundtrips(self, repo: PizzaRepository):
        pizza = _make_pizza("Margherita")
        await repo.add(pizza)
        fetched = await repo.get(pizza.id)
        assert fetched is not None
        assert fetched.id == pizza.id
        assert fetched.name == "Margherita"
        assert fetched.price.amount == Decimal("8.50")
        assert fetched.price.currency == "EUR"
        assert fetched.allergens == frozenset({Allergen.gluten, Allergen.milk})
        assert fetched.ingredients == ["tomato", "mozzarella"]
        assert fetched.available is True

    async def test_get_missing_returns_none(self, repo: PizzaRepository):
        assert await repo.get(uuid4()) is None

    async def test_list_empty(self, repo: PizzaRepository):
        assert await repo.list() == []

    async def test_list_populated_includes_unavailable(self, repo: PizzaRepository):
        p1 = _make_pizza("A", available=True)
        p2 = _make_pizza("B", available=False)
        await repo.add(p1)
        await repo.add(p2)
        all_pizzas = await repo.list()
        assert {p.name for p in all_pizzas} == {"A", "B"}

    async def test_list_only_available_filters_unavailable(self, repo: PizzaRepository):
        p1 = _make_pizza("A", available=True)
        p2 = _make_pizza("B", available=False)
        await repo.add(p1)
        await repo.add(p2)
        available = await repo.list(only_available=True)
        assert {p.name for p in available} == {"A"}

    async def test_update_persists_changes(self, repo: PizzaRepository):
        pizza = _make_pizza("Original")
        await repo.add(pizza)
        pizza.rename("Renamed")
        pizza.change_price(Money(amount=Decimal("9.99"), currency="EUR"))
        pizza.mark_unavailable()
        await repo.update(pizza)
        fetched = await repo.get(pizza.id)
        assert fetched is not None
        assert fetched.name == "Renamed"
        assert fetched.price.amount == Decimal("9.99")
        assert fetched.available is False

    async def test_delete_removes_existing(self, repo: PizzaRepository):
        pizza = _make_pizza("Margherita")
        await repo.add(pizza)
        await repo.delete(pizza.id)
        assert await repo.get(pizza.id) is None

    async def test_delete_missing_is_silent(self, repo: PizzaRepository):
        # Spec: delete is idempotent — no error when the id is unknown.
        await repo.delete(uuid4())

    async def test_find_by_name_hit(self, repo: PizzaRepository):
        pizza = _make_pizza("Diavola")
        await repo.add(pizza)
        found = await repo.find_by_name("Diavola")
        assert found is not None
        assert found.id == pizza.id

    async def test_find_by_name_miss_returns_none(self, repo: PizzaRepository):
        assert await repo.find_by_name("nope") is None

    async def test_find_by_name_is_case_sensitive(self, repo: PizzaRepository):
        # The Protocol doesn't promise case-insensitivity; lock the behavior.
        pizza = _make_pizza("Margherita")
        await repo.add(pizza)
        assert await repo.find_by_name("margherita") is None
        assert await repo.find_by_name("Margherita") is not None
