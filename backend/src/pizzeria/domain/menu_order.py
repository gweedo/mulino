from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID


class InvalidMenuOrder(ValueError):
    """A requested Menu Order does not list every Pizza of the Menu exactly once."""


@dataclass(frozen=True)
class MenuOrder:
    """The sequence in which the Menu lists its Pizzas (see CONTEXT.md)."""

    pizza_ids: tuple[UUID, ...]

    @staticmethod
    def rearrange(current: Sequence[UUID], requested: Sequence[UUID]) -> "MenuOrder":
        """Accept `requested` only if it is a permutation of the `current` Menu."""
        if len(set(requested)) != len(requested):
            raise InvalidMenuOrder("Menu order lists a pizza more than once")
        if set(requested) != set(current):
            raise InvalidMenuOrder("Menu order does not match the current menu")
        return MenuOrder(pizza_ids=tuple(requested))
