from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.pizza import Pizza
from pizzeria.infrastructure.mappers import (
    apply_pizza_to_orm,
    pizza_from_orm,
    pizza_to_orm,
)
from pizzeria.infrastructure.models import PizzaORM


class SqlPizzaRepository(PizzaRepository):
    """PostgreSQL-backed PizzaRepository.

    Operates on an injected AsyncSession; the session lifecycle (commit /
    rollback) is owned by the caller (API layer or test fixture).
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, pizza: Pizza) -> None:
        self._session.add(pizza_to_orm(pizza))
        await self._session.flush()

    async def get(self, pizza_id: UUID) -> Pizza | None:
        orm = await self._session.get(PizzaORM, pizza_id)
        return pizza_from_orm(orm) if orm else None

    async def list(self, *, only_available: bool = False) -> list[Pizza]:
        stmt = select(PizzaORM).order_by(PizzaORM.position, PizzaORM.id)
        if only_available:
            stmt = stmt.where(PizzaORM.available.is_(True))
        result = await self._session.execute(stmt)
        return [pizza_from_orm(orm) for orm in result.scalars().all()]

    async def reorder(self, pizza_ids: Sequence[UUID]) -> None:
        # New rows take their position from a sequence that is always ahead of
        # 0..n-1, so pizzas added after a reorder still land at the end.
        result = await self._session.execute(select(PizzaORM))
        rows = {orm.id: orm for orm in result.scalars().all()}
        for index, pizza_id in enumerate(pizza_ids):
            rows[pizza_id].position = index
        await self._session.flush()

    async def update(self, pizza: Pizza) -> None:
        orm = await self._session.get(PizzaORM, pizza.id)
        if orm is None:
            # Spec for update is not explicit; the application layer guards via
            # PizzaNotFound. The SQL repo treats unknown id as a no-op to keep
            # parity with the InMemory contract behavior on add/update.
            return
        apply_pizza_to_orm(pizza, orm)
        await self._session.flush()

    async def delete(self, pizza_id: UUID) -> None:
        orm = await self._session.get(PizzaORM, pizza_id)
        if orm is None:
            return  # idempotent per contract test
        await self._session.delete(orm)
        await self._session.flush()

    async def find_by_name(self, name: str) -> Pizza | None:
        stmt = select(PizzaORM).where(PizzaORM.name == name)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return pizza_from_orm(orm) if orm else None
