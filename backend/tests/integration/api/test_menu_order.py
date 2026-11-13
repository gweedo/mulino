"""Integration tests for reordering the Menu (PUT /api/admin/pizzas/order)."""

from decimal import Decimal
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric import ec
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.infrastructure.models import PizzaORM
from tests._auth import sign_token


async def _insert(session: AsyncSession, name: str, *, available: bool = True) -> PizzaORM:
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


async def test_reorder_changes_admin_and_public_order(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    a = await _insert(session, "A")
    b = await _insert(session, "B", available=False)
    c = await _insert(session, "C")

    resp = await client.put(
        "/api/admin/pizzas/order",
        json={"pizza_ids": [str(c.id), str(b.id), str(a.id)]},
        headers=auth_headers,
    )
    assert resp.status_code == 204

    admin = await client.get("/api/admin/pizzas", headers=auth_headers)
    assert [p["name"] for p in admin.json()] == ["C", "B", "A"]
    public = await client.get("/api/pizzas")
    assert [p["name"] for p in public.json()] == ["C", "A"]


async def test_reorder_that_does_not_match_the_menu_returns_409(
    client: AsyncClient, session: AsyncSession, auth_headers: dict[str, str]
) -> None:
    a = await _insert(session, "A")
    await _insert(session, "B")

    resp = await client.put(
        "/api/admin/pizzas/order", json={"pizza_ids": [str(a.id)]}, headers=auth_headers
    )

    assert resp.status_code == 409
    admin = await client.get("/api/admin/pizzas", headers=auth_headers)
    assert [p["name"] for p in admin.json()] == ["A", "B"]


async def test_reorder_with_malformed_body_returns_422(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    resp = await client.put(
        "/api/admin/pizzas/order", json={"pizza_ids": ["not-a-uuid"]}, headers=auth_headers
    )
    assert resp.status_code == 422


async def test_reorder_without_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.put("/api/admin/pizzas/order", json={"pizza_ids": []})
    assert resp.status_code == 401


async def test_reorder_without_menu_manager_role_returns_403(
    client: AsyncClient, signing_key: ec.EllipticCurvePrivateKey
) -> None:
    token = sign_token(signing_key, role=None)
    resp = await client.put(
        "/api/admin/pizzas/order",
        json={"pizza_ids": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
