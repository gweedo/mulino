"""Run the repository contract against InMemoryPizzaRepository."""

import pytest

from pizzeria.infrastructure.repositories.in_memory_pizza_repository import (
    InMemoryPizzaRepository,
)
from tests._contracts.pizza_repository_contract import PizzaRepositoryContract


class TestInMemoryPizzaRepository(PizzaRepositoryContract):
    @pytest.fixture
    async def repo(self) -> InMemoryPizzaRepository:
        return InMemoryPizzaRepository()
