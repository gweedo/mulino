from pizzeria.domain.allergen import Allergen
from pizzeria.domain.money import Money
from pizzeria.domain.owner import Owner
from pizzeria.domain.pizza import Pizza
from pizzeria.infrastructure.models import OwnerORM, PizzaORM


def pizza_to_orm(pizza: Pizza) -> PizzaORM:
    return PizzaORM(
        id=pizza.id,
        name=pizza.name,
        description=pizza.description,
        ingredients=list(pizza.ingredients),
        allergens=sorted(a.value for a in pizza.allergens),
        price_amount=pizza.price.amount,
        price_currency=pizza.price.currency,
        available=pizza.available,
    )


def pizza_from_orm(orm: PizzaORM) -> Pizza:
    return Pizza(
        id=orm.id,
        name=orm.name,
        description=orm.description,
        ingredients=list(orm.ingredients),
        allergens=frozenset(Allergen(a) for a in orm.allergens),
        price=Money(amount=orm.price_amount, currency=orm.price_currency),
        available=orm.available,
    )


def apply_pizza_to_orm(pizza: Pizza, orm: PizzaORM) -> None:
    """Copy a domain Pizza onto an existing ORM row (used by update)."""
    orm.name = pizza.name
    orm.description = pizza.description
    orm.ingredients = list(pizza.ingredients)
    orm.allergens = sorted(a.value for a in pizza.allergens)
    orm.price_amount = pizza.price.amount
    orm.price_currency = pizza.price.currency
    orm.available = pizza.available


def owner_from_orm(orm: OwnerORM) -> Owner:
    return Owner(id=orm.id, email=orm.email, password_hash=orm.password_hash)
