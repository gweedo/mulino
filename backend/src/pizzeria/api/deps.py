"""FastAPI dependency functions."""

from __future__ import annotations

import functools
from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.menu_manager import MenuManager
from pizzeria.infrastructure.db import make_engine, make_session_factory
from pizzeria.infrastructure.repositories.pizza_repository import SqlPizzaRepository
from pizzeria.infrastructure.security.supabase_jwt import (
    ExpiredTokenError,
    InvalidTokenError,
    KeySource,
    jwks_key_source,
    verify_access_token,
)
from pizzeria.infrastructure.settings import get_settings

# Role granted in the Supabase dashboard via app_metadata (ADR 0003).
MENU_MANAGER_ROLE = "menu_manager"

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


PizzaRepoDep = Annotated[PizzaRepository, Depends(get_pizza_repo)]


@functools.cache
def get_key_source() -> KeySource:
    """Public keys of the Supabase project; one cached JWKS client per process."""
    return jwks_key_source(get_settings().supabase_jwks_url)


_bearer = HTTPBearer(auto_error=False)


def get_current_menu_manager(
    key_source: Annotated[KeySource, Depends(get_key_source)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> MenuManager:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        claims = verify_access_token(
            credentials.credentials,
            key_source=key_source,
            issuer=get_settings().supabase_auth_issuer,
        )
    except ExpiredTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired"
        ) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        ) from exc

    # app_metadata is admin-only; user_metadata is user-editable and never consulted.
    app_metadata = claims.get("app_metadata") or {}
    if app_metadata.get("role") != MENU_MANAGER_ROLE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a menu manager")

    try:
        return MenuManager(id=UUID(claims["sub"]), email=claims.get("email", ""))
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session"
        ) from exc


CurrentMenuManager = Annotated[MenuManager, Depends(get_current_menu_manager)]
