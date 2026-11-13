from uuid import UUID

from pizzeria.application.ports.pizza_repository import PizzaRepository
from pizzeria.domain.menu_order import MenuOrder


class ReorderMenu:
    """Use case: change the order in which the Menu lists its pizzas."""

    def __init__(self, repository: PizzaRepository):
        self.repository = repository

    async def execute(self, pizza_ids: list[UUID]) -> None:
        """Raises InvalidMenuOrder unless `pizza_ids` lists every pizza exactly once."""
        current = [p.id for p in await self.repository.list()]
        order = MenuOrder.rearrange(current=current, requested=pizza_ids)
        await self.repository.reorder(list(order.pizza_ids))
