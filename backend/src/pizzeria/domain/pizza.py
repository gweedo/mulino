from uuid import UUID, uuid4

from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money


class Pizza:
    def __init__(
        self,
        id: UUID,
        name: str,
        description: str,
        ingredients: list[str],
        allergens: frozenset[Allergen],
        price: Money,
        available: bool,
    ):
        self._id = id
        self._name = name
        self._description = description
        self._ingredients = ingredients
        self._allergens = allergens
        self._price = price
        self._available = available

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def ingredients(self) -> list[str]:
        return list(self._ingredients)

    @property
    def allergens(self) -> frozenset[Allergen]:
        return self._allergens

    @property
    def price(self) -> Money:
        return self._price

    @property
    def available(self) -> bool:
        return self._available

    @staticmethod
    def create(
        name: str,
        description: str,
        ingredients: list[str],
        allergens: set[Allergen] | frozenset[Allergen],
        price: Money,
    ) -> "Pizza":
        """Factory method to create a new Pizza with validation."""
        Pizza._validate_name(name)
        Pizza._validate_ingredients(ingredients)
        Pizza._validate_allergens(allergens)

        return Pizza(
            id=uuid4(),
            name=name,
            description=description,
            ingredients=ingredients,
            allergens=frozenset(allergens),
            price=price,
            available=True,
        )

    def mark_available(self) -> None:
        self._available = True

    def mark_unavailable(self) -> None:
        self._available = False

    def rename(self, new_name: str) -> None:
        """Rename the pizza with validation."""
        Pizza._validate_name(new_name)
        self._name = new_name

    def change_price(self, new_price: Money) -> None:
        """Update the pizza price."""
        self._price = new_price

    def change_description(self, new_description: str) -> None:
        self._description = new_description

    def change_ingredients(self, new_ingredients: list[str]) -> None:
        Pizza._validate_ingredients(new_ingredients)
        self._ingredients = list(new_ingredients)

    def change_allergens(
        self, new_allergens: set[Allergen] | frozenset[Allergen]
    ) -> None:
        Pizza._validate_allergens(new_allergens)
        self._allergens = frozenset(new_allergens)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name:
            raise ValueError("name must not be empty")
        if len(name) > 80:
            raise ValueError("name must be at most 80 characters")

    @staticmethod
    def _validate_ingredients(ingredients: list[str]) -> None:
        if not ingredients:
            raise ValueError("Pizza must have at least 1 ingredient")

    @staticmethod
    def _validate_allergens(allergens: set[Allergen] | frozenset[Allergen]) -> None:
        for allergen in allergens:
            if not isinstance(allergen, Allergen):
                raise ValueError("All allergens must be Allergen enum members")
