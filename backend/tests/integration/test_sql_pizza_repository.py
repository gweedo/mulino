"""Run the repository contract against SqlPizzaRepository (real Postgres)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from pizzeria.infrastructure.repositories.pizza_repository import SqlPizzaRepository
from tests._contracts.pizza_repository_contract import PizzaRepositoryContract


class TestSqlPizzaRepository(PizzaRepositoryContract):
    @pytest.fixture
    async def repo(self, session: AsyncSession) -> SqlPizzaRepository:
        return SqlPizzaRepository(session)
