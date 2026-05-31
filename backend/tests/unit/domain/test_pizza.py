from decimal import Decimal
from uuid import UUID

import pytest

from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.domain.pizza import Pizza


def test_pizza_create():
    """Pizza.create() returns a new Pizza with valid data."""
    p = Pizza.create(
        name="Margherita",
        description="Classic pizza",
        ingredients=["tomato", "mozzarella"],
        allergens={Allergen.milk},
        price=Money(Decimal("10.00"), "EUR"),
    )
    assert p.name == "Margherita"
    assert p.description == "Classic pizza"
    assert p.ingredients == ["tomato", "mozzarella"]
    assert p.allergens == frozenset({Allergen.milk})
    assert p.price == Money(Decimal("10.00"), "EUR")
    assert p.available is True
    assert isinstance(p.id, UUID)


def test_pizza_name_non_empty():
    """Pizza name must not be empty."""
    with pytest.raises(ValueError, match="name must not be empty"):
        Pizza.create(
            name="",
            description="",
            ingredients=["x"],
            allergens=set(),
            price=Money(Decimal("10"), "EUR"),
        )


def test_pizza_name_max_80_chars():
    """Pizza name must be at most 80 characters."""
    long_name = "x" * 81
    with pytest.raises(ValueError, match="name must be at most 80 characters"):
        Pizza.create(
            name=long_name,
            description="",
            ingredients=["x"],
            allergens=set(),
            price=Money(Decimal("10"), "EUR"),
        )

    valid_name = "x" * 80
    p = Pizza.create(
        name=valid_name,
        description="",
        ingredients=["x"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )
    assert p.name == valid_name


def test_pizza_at_least_one_ingredient():
    """Pizza must have at least one ingredient."""
    with pytest.raises(ValueError, match="must have at least 1 ingredient"):
        Pizza.create(
            name="Bad Pizza",
            description="",
            ingredients=[],
            allergens=set(),
            price=Money(Decimal("10"), "EUR"),
        )


def test_pizza_allergens_is_frozenset():
    """Pizza allergens must be a frozenset of Allergen enum members."""
    p = Pizza.create(
        name="Pizza",
        description="",
        ingredients=["x"],
        allergens={Allergen.gluten, Allergen.milk},
        price=Money(Decimal("10"), "EUR"),
    )
    assert isinstance(p.allergens, frozenset)
    assert Allergen.gluten in p.allergens
    assert Allergen.milk in p.allergens


def test_pizza_allergens_no_duplicates():
    """Allergens are deduplicated (frozenset handles this)."""
    p = Pizza.create(
        name="Pizza",
        description="",
        ingredients=["x"],
        allergens={Allergen.milk, Allergen.milk},
        price=Money(Decimal("10"), "EUR"),
    )
    assert len(p.allergens) == 1


def test_pizza_mark_available():
    """mark_available() sets available to True."""
    p = Pizza.create(
        name="Pizza",
        description="",
        ingredients=["x"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )
    assert p.available is True
    p.mark_unavailable()
    assert p.available is False
    p.mark_available()
    assert p.available is True


def test_pizza_mark_unavailable():
    """mark_unavailable() sets available to False."""
    p = Pizza.create(
        name="Pizza",
        description="",
        ingredients=["x"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )
    p.mark_unavailable()
    assert p.available is False


def test_pizza_rename():
    """rename() changes the pizza name with validation."""
    p = Pizza.create(
        name="Original",
        description="",
        ingredients=["x"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )
    p.rename("New Name")
    assert p.name == "New Name"

    with pytest.raises(ValueError, match="name must not be empty"):
        p.rename("")


def test_pizza_change_price():
    """change_price() updates the price."""
    p = Pizza.create(
        name="Pizza",
        description="",
        ingredients=["x"],
        allergens=set(),
        price=Money(Decimal("10.00"), "EUR"),
    )
    new_price = Money(Decimal("15.00"), "EUR")
    p.change_price(new_price)
    assert p.price == new_price


def test_pizza_change_description():
    """change_description() updates the description."""
    p = Pizza.create(
        name="Pizza",
        description="old",
        ingredients=["x"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )
    p.change_description("new")
    assert p.description == "new"


def test_pizza_change_ingredients():
    """change_ingredients() replaces ingredients with validation."""
    p = Pizza.create(
        name="Pizza",
        description="",
        ingredients=["tomato"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )
    p.change_ingredients(["tomato", "cheese"])
    assert p.ingredients == ["tomato", "cheese"]

    with pytest.raises(ValueError, match="at least 1 ingredient"):
        p.change_ingredients([])


def test_pizza_change_allergens():
    """change_allergens() replaces allergens with validation."""
    p = Pizza.create(
        name="Pizza",
        description="",
        ingredients=["x"],
        allergens={Allergen.milk},
        price=Money(Decimal("10"), "EUR"),
    )
    p.change_allergens({Allergen.gluten, Allergen.eggs})
    assert p.allergens == frozenset({Allergen.gluten, Allergen.eggs})

    with pytest.raises(ValueError, match="must be Allergen enum members"):
        p.change_allergens({"milk"})  # type: ignore


def test_pizza_ingredients_property_returns_copy():
    """Mutating the returned ingredients list must not affect the aggregate."""
    p = Pizza.create(
        name="X",
        description="",
        ingredients=["tomato"],
        allergens=set(),
        price=Money(Decimal("10"), "EUR"),
    )
    p.ingredients.append("hacked")
    assert p.ingredients == ["tomato"]


def test_pizza_allergens_must_be_enum_members():
    """Allergens must be Allergen enum members, not strings."""
    with pytest.raises(ValueError, match="must be Allergen enum members"):
        Pizza.create(
            name="Pizza",
            description="",
            ingredients=["x"],
            allergens={"milk"},  # type: ignore
            price=Money(Decimal("10"), "EUR"),
        )
