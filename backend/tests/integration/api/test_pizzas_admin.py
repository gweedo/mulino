"""Integration tests for admin pizza endpoints."""

from decimal import Decimal
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.infrastructure.models import PizzaORM

_PIZZA_IN = {
    "name": "Test Pizza",
    "description": "A test pizza",
    "ingredients": ["flour", "tomato"],
    "allergens": ["gluten"],
    "price_amount": "9.99",
    "price_currency": "EUR",
}


async def _insert_pizza(
    session: AsyncSession,
    *,
    name: str = "Existing Pizza",
    available: bool = True,
) -> PizzaORM:
    p = PizzaORM(
        id=uuid4(),
        name=name,
        description="desc",
        ingredients=["tomato"],
        allergens=[],
        price_amount=Decimal("8.00"),
        price_currency="EUR",
        available=available,
    )
    session.add(p)
    await session.flush()
    return p


# ── List ────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_admin_list_includes_unavailable(
    client: AsyncClient, session: AsyncSession, auth_cookie: str
) -> None:
    await _insert_pizza(session, name="Visible", available=True)
    await _insert_pizza(session, name="Hidden", available=False)
    client.cookies.set("session", auth_cookie)
    resp = await client.get("/api/admin/pizzas")
    assert resp.status_code == 200
    names = [p["name"] for p in resp.json()]
    assert "Visible" in names
    assert "Hidden" in names


@pytest.mark.asyncio
async def test_admin_list_without_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/api/admin/pizzas")
    assert resp.status_code == 401


# ── Create ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_pizza_returns_201(
    client: AsyncClient, auth_cookie: str
) -> None:
    client.cookies.set("session", auth_cookie)
    resp = await client.post("/api/pizzas", json=_PIZZA_IN)
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == _PIZZA_IN["name"]
    assert body["available"] is True


@pytest.mark.asyncio
async def test_create_duplicate_name_returns_409(
    client: AsyncClient, session: AsyncSession, auth_cookie: str
) -> None:
    await _insert_pizza(session, name=_PIZZA_IN["name"])
    client.cookies.set("session", auth_cookie)
    resp = await client.post("/api/pizzas", json=_PIZZA_IN)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_invalid_allergen_returns_422(
    client: AsyncClient, auth_cookie: str
) -> None:
    client.cookies.set("session", auth_cookie)
    bad = {**_PIZZA_IN, "allergens": ["not-an-allergen"]}
    resp = await client.post("/api/pizzas", json=bad)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_without_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.post("/api/pizzas", json=_PIZZA_IN)
    assert resp.status_code == 401


# ── Update ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_name_returns_204_and_reflects_in_admin_list(
    client: AsyncClient, session: AsyncSession, auth_cookie: str
) -> None:
    p = await _insert_pizza(session)
    client.cookies.set("session", auth_cookie)
    resp = await client.put(f"/api/pizzas/{p.id}", json={"name": "Renamed Pizza"})
    assert resp.status_code == 204
    list_resp = await client.get("/api/admin/pizzas")
    names = [x["name"] for x in list_resp.json()]
    assert "Renamed Pizza" in names


@pytest.mark.asyncio
async def test_update_available_false_hides_from_public(
    client: AsyncClient, session: AsyncSession, auth_cookie: str
) -> None:
    p = await _insert_pizza(session, available=True)
    client.cookies.set("session", auth_cookie)
    await client.put(f"/api/pizzas/{p.id}", json={"available": False})
    public_resp = await client.get(f"/api/pizzas/{p.id}")
    assert public_resp.status_code == 404
    admin_resp = await client.get("/api/admin/pizzas")
    ids = [x["id"] for x in admin_resp.json()]
    assert str(p.id) in ids


@pytest.mark.asyncio
async def test_update_price_missing_currency_returns_422(
    client: AsyncClient, session: AsyncSession, auth_cookie: str
) -> None:
    p = await _insert_pizza(session)
    client.cookies.set("session", auth_cookie)
    resp = await client.put(f"/api/pizzas/{p.id}", json={"price_amount": "15.00"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_missing_pizza_returns_404(
    client: AsyncClient, auth_cookie: str
) -> None:
    client.cookies.set("session", auth_cookie)
    resp = await client.put(f"/api/pizzas/{uuid4()}", json={"name": "Ghost"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_without_auth_returns_401(
    client: AsyncClient, session: AsyncSession
) -> None:
    p = await _insert_pizza(session)
    resp = await client.put(f"/api/pizzas/{p.id}", json={"name": "NoAuth"})
    assert resp.status_code == 401


# ── Delete ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_returns_204_and_pizza_becomes_404(
    client: AsyncClient, session: AsyncSession, auth_cookie: str
) -> None:
    p = await _insert_pizza(session)
    client.cookies.set("session", auth_cookie)
    resp = await client.delete(f"/api/pizzas/{p.id}")
    assert resp.status_code == 204
    assert (await client.get(f"/api/pizzas/{p.id}")).status_code == 404


@pytest.mark.asyncio
async def test_delete_missing_returns_404(
    client: AsyncClient, auth_cookie: str
) -> None:
    client.cookies.set("session", auth_cookie)
    resp = await client.delete(f"/api/pizzas/{uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_without_auth_returns_401(
    client: AsyncClient, session: AsyncSession
) -> None:
    p = await _insert_pizza(session)
    resp = await client.delete(f"/api/pizzas/{p.id}")
    assert resp.status_code == 401
