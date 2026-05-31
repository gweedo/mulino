"""Idempotent owner seed script.

Usage:
    OWNER_EMAIL=x@y.z OWNER_PASSWORD=secret uv run python -m pizzeria.seed_owner

Set OWNER_FORCE_RESET=1 to overwrite an existing owner's password_hash
(used for password rotation / recovery).
"""

import asyncio
import os
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.infrastructure.db import make_engine, make_session_factory
from pizzeria.infrastructure.models import OwnerORM
from pizzeria.infrastructure.security.passwords import hash_password


async def seed_owner(
    session: AsyncSession,
    *,
    email: str,
    password: str,
    force_reset: bool = False,
) -> str:
    """Create or update the single Owner row.

    Returns "created" | "updated" | "noop".
    """
    existing = (
        await session.execute(select(OwnerORM).where(OwnerORM.email == email))
    ).scalar_one_or_none()

    if existing is None:
        session.add(
            OwnerORM(id=uuid4(), email=email, password_hash=hash_password(password))
        )
        await session.flush()
        return "created"

    if force_reset:
        existing.password_hash = hash_password(password)
        await session.flush()
        return "updated"

    return "noop"


def _require_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"{name} environment variable is required")
    return val


async def _main_async() -> None:
    email = _require_env("OWNER_EMAIL")
    password = _require_env("OWNER_PASSWORD")
    force_reset = os.environ.get("OWNER_FORCE_RESET") == "1"

    engine = make_engine()
    factory = make_session_factory(engine)
    try:
        async with factory() as session:
            result = await seed_owner(
                session, email=email, password=password, force_reset=force_reset
            )
            await session.commit()
            print(f"seed_owner: {result} ({email})")
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
