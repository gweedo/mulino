from enum import StrEnum

from pizzeria.domain.allergen import Allergen


def test_allergen_members():
    """Allergen has all EU 14 allergens."""
    expected = {
        "gluten",
        "crustaceans",
        "eggs",
        "fish",
        "peanuts",
        "soy",
        "milk",
        "nuts",
        "celery",
        "mustard",
        "sesame",
        "sulphites",
        "lupin",
        "molluscs",
    }
    assert set(a.value for a in Allergen) == expected


def test_allergen_is_str_enum():
    """Allergen is a StrEnum."""
    assert issubclass(Allergen, StrEnum)


def test_allergen_value_equality():
    """Allergen members can be compared by value."""
    assert Allergen.gluten.value == "gluten"
    assert Allergen.milk.value == "milk"
