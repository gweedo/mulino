"""Integration tests for /api/auth endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_valid_returns_200_with_session_cookie(
    client: AsyncClient, test_owner: dict
) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": test_owner["email"], "password": test_owner["password"]},
    )
    assert resp.status_code == 200
    assert "session" in resp.cookies


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(
    client: AsyncClient, test_owner: dict
) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": test_owner["email"], "password": "wrongpassword"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_rate_limited_after_five_requests(
    client: AsyncClient, test_owner: dict
) -> None:
    payload = {"email": test_owner["email"], "password": "wrong"}
    for _ in range(5):
        await client.post("/api/auth/login", json=payload)
    resp = await client.post("/api/auth/login", json=payload)
    assert resp.status_code == 429
    assert "detail" in resp.json()


@pytest.mark.asyncio
async def test_logout_with_auth_returns_204_and_clears_cookie(
    client: AsyncClient, auth_cookie: str
) -> None:
    client.cookies.set("session", auth_cookie)
    resp = await client.post("/api/auth/logout")
    assert resp.status_code == 204
    # Cookie should be cleared (max-age=0 or empty value)
    set_cookie = resp.headers.get("set-cookie", "")
    assert "session" in set_cookie


@pytest.mark.asyncio
async def test_logout_without_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.post("/api/auth/logout")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_auth_returns_200_with_id_and_email(
    client: AsyncClient, auth_cookie: str, test_owner: dict
) -> None:
    client.cookies.set("session", auth_cookie)
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == test_owner["email"]
    assert str(body["id"]) == str(test_owner["id"])


@pytest.mark.asyncio
async def test_me_without_auth_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_expired_token_returns_401(client: AsyncClient) -> None:
    import time

    from jose import jwt as jose_jwt

    from pizzeria.infrastructure.settings import get_settings

    s = get_settings()
    expired_token = jose_jwt.encode(
        {"sub": "owner@pizzeria.test", "exp": int(time.time()) - 60},
        s.JWT_SECRET,
        algorithm=s.JWT_ALG,
    )
    client.cookies.set("session", expired_token)
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_garbage_cookie_returns_401(client: AsyncClient) -> None:
    client.cookies.set("session", "not.a.jwt.token")
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401
