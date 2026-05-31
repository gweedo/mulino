"""FastAPI dependency functions."""

from __future__ import annotations

import functools
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.application.ports.owner_repository import OwnerRepository
from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.application.use_cases.authenticate_owner import AuthenticateOwner
from pizzeria.domain.owner import Owner
from pizzeria.infrastructure.db import make_engine, make_session_factory
from pizzeria.infrastructure.repositories.owner_repository import SqlOwnerRepository
from pizzeria.infrastructure.repositories.pizza_repository import SqlPizzaRepository
from pizzeria.infrastructure.security.jwt import (
    ExpiredTokenError,
    InvalidTokenError,
    decode_token,
    encode_token,
)
from pizzeria.infrastructure.security.passwords import verify_password
from pizzeria.infrastructure.settings import get_settings

_engine: object = None
_factory: object = None


def _get_factory():  # type: ignore[return]
    global _engine, _factory
    if _factory is None:
        _engine = make_engine()
        _factory = make_session_factory(_engine)  # type: ignore[arg-type]
    return _factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _get_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_pizza_repo(session: SessionDep) -> PizzaRepository:
    return SqlPizzaRepository(session)


def get_owner_repo(session: SessionDep) -> OwnerRepository:
    return SqlOwnerRepository(session)


PizzaRepoDep = Annotated[PizzaRepository, Depends(get_pizza_repo)]
OwnerRepoDep = Annotated[OwnerRepository, Depends(get_owner_repo)]


def get_auth_use_case(repo: OwnerRepoDep) -> AuthenticateOwner:
    s = get_settings()
    bound_encode = functools.partial(
        encode_token,
        secret=s.JWT_SECRET,
        algorithm=s.JWT_ALG,
        ttl_minutes=s.JWT_TTL_MIN,
    )
    return AuthenticateOwner(repo, verify_password, bound_encode)


async def get_current_owner(
    owner_repo: OwnerRepoDep,
    session_cookie: Annotated[str | None, Cookie(alias="session")] = None,
) -> Owner:
    if session_cookie is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        settings = get_settings()
        payload = decode_token(
            session_cookie,
            secret=settings.JWT_SECRET,
            algorithm=settings.JWT_ALG,
        )
    except ExpiredTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        ) from exc

    email: str | None = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

    owner = await owner_repo.get_by_email(email)
    if owner is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return owner


CurrentOwner = Annotated[Owner, Depends(get_current_owner)]


def cookie_secure(request: Request) -> bool:
    return request.url.scheme == "https"
