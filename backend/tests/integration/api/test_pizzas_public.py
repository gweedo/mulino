"""Integration tests for public pizza endpoints."""

from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.infrastructure.models import PizzaORM


async def _insert_pizza(
    session: AsyncSession,
    *,
    name: str = "Margherita",
    available: bool = True,
    price_amount: Decimal = Decimal("10.00"),
) -> PizzaORM:
    p = PizzaORM(
        id=uuid4(),
        name=name,
        description="Classic tomato and mozzarella",
        ingredients=["tomato", "mozzarella"],
        allergens=["gluten", "milk"],
        price_amount=price_amount,
        price_currency="EUR",
        available=available,
    )
    session.add(p)
    await session.flush()
    return p


@pytest.mark.asyncio
async def test_list_returns_only_available_pizzas(
    client: AsyncClient, session: AsyncSession
) -> None:
    await _insert_pizza(session, name="Available Pizza", available=True)
    await _insert_pizza(session, name="Hidden Pizza", available=False)
    resp = await client.get("/api/pizzas")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "Available Pizza" in names
    assert "Hidden Pizza" not in names


@pytest.mark.asyncio
async def test_list_with_no_pizzas_returns_empty(client: AsyncClient) -> None:
    resp = await client.get("/api/pizzas")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_available_pizza_returns_200(
    client: AsyncClient, session: AsyncSession
) -> None:
    p = await _insert_pizza(session, available=True)
    resp = await client.get(f"/api/pizzas/{p.id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == str(p.id)


@pytest.mark.asyncio
async def test_get_unknown_id_returns_404(client: AsyncClient) -> None:
    resp = await client.get(f"/api/pizzas/{uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_unavailable_pizza_returns_404(
    client: AsyncClient, session: AsyncSession
) -> None:
    p = await _insert_pizza(session, available=False)
    resp = await client.get(f"/api/pizzas/{p.id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_price_is_nested_object(
    client: AsyncClient, session: AsyncSession
) -> None:
    await _insert_pizza(session, price_amount=Decimal("12.50"))
    resp = await client.get("/api/pizzas")
    assert resp.status_code == 200
    price = resp.json()[0]["price"]
    assert "amount" in price
    assert "currency" in price
    assert price["currency"] == "EUR"


@pytest.mark.asyncio
async def test_allergens_are_sorted_string_list(
    client: AsyncClient, session: AsyncSession
) -> None:
    await _insert_pizza(session)
    resp = await client.get("/api/pizzas")
    allergens = resp.json()[0]["allergens"]
    assert isinstance(allergens, list)
    assert allergens == sorted(allergens)
