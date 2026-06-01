"""Idempotent pizza seed script for development.

Usage:
    uv run python -m pizzeria.seed_pizzas

Skips any pizza that already exists by name, so it is safe to re-run.
"""

import asyncio
from dataclasses import dataclass, field
from decimal import Decimal

from pizzeria.application.errors import DuplicatePizzaName
from pizzeria.application.use_cases.create_pizza import CreatePizza
from pizzeria.infrastructure.db import make_engine, make_session_factory
from pizzeria.infrastructure.repositories.pizza_repository import SqlPizzaRepository


@dataclass
class PizzaSeed:
    name: str
    description: str
    ingredients: list[str]
    allergens: list[str]
    price_amount: Decimal
    price_currency: str = field(default="EUR")


PIZZAS: list[PizzaSeed] = [
    PizzaSeed(
        name="Margherita",
        description="Il classico senza tempo. Pomodoro San Marzano, fior di latte, basilico fresco.",
        ingredients=["farina 00", "pomodoro San Marzano", "fior di latte", "basilico", "olio EVO"],
        allergens=["gluten", "milk"],
        price_amount=Decimal("9.50"),
    ),
    PizzaSeed(
        name="Marinara",
        description="La più antica. Solo pomodoro, aglio, origano e olio — niente formaggio.",
        ingredients=["farina 00", "pomodoro San Marzano", "aglio", "origano", "olio EVO"],
        allergens=["gluten"],
        price_amount=Decimal("8.00"),
    ),
    PizzaSeed(
        name="Diavola",
        description="Salame piccante, pomodoro, fior di latte. Per chi ama il fuoco.",
        ingredients=["farina 00", "pomodoro", "fior di latte", "salame piccante", "olio EVO"],
        allergens=["gluten", "milk"],
        price_amount=Decimal("11.00"),
    ),
    PizzaSeed(
        name="Napoli",
        description="Pomodoro, mozzarella, alici di Cetara, capperi di Pantelleria.",
        ingredients=["farina 00", "pomodoro", "mozzarella", "alici", "capperi", "olio EVO"],
        allergens=["gluten", "milk", "fish"],
        price_amount=Decimal("12.00"),
    ),
    PizzaSeed(
        name="Quattro Formaggi",
        description="Fior di latte, gorgonzola, parmigiano, provola affumicata.",
        ingredients=["farina 00", "fior di latte", "gorgonzola", "parmigiano", "provola affumicata"],
        allergens=["gluten", "milk"],
        price_amount=Decimal("13.50"),
    ),
    PizzaSeed(
        name="Capricciosa",
        description="Pomodoro, mozzarella, prosciutto cotto, funghi, carciofi, olive nere.",
        ingredients=[
            "farina 00", "pomodoro", "mozzarella", "prosciutto cotto",
            "funghi", "carciofi", "olive nere",
        ],
        allergens=["gluten", "milk"],
        price_amount=Decimal("12.50"),
    ),
    PizzaSeed(
        name="Bufalina",
        description="Pomodoro San Marzano, mozzarella di bufala DOP, basilico. Ingredienti e nient'altro.",
        ingredients=["farina 00", "pomodoro San Marzano", "mozzarella di bufala DOP", "basilico"],
        allergens=["gluten", "milk"],
        price_amount=Decimal("14.00"),
    ),
]


async def _seed(session, *, pizzas: list[PizzaSeed] = PIZZAS) -> dict[str, str]:
    """Seed the pizza catalog. Returns {name: 'created' | 'skipped'}."""
    repo = SqlPizzaRepository(session)
    use_case = CreatePizza(repo)
    results: dict[str, str] = {}

    for p in pizzas:
        try:
            await use_case.execute(
                name=p.name,
                description=p.description,
                ingredients=p.ingredients,
                allergen_names=p.allergens,
                price_amount=p.price_amount,
                price_currency=p.price_currency,
            )
            results[p.name] = "created"
        except DuplicatePizzaName:
            results[p.name] = "skipped"

    return results


async def _main_async() -> None:
    engine = make_engine()
    factory = make_session_factory(engine)
    try:
        async with factory() as session:
            results = await _seed(session)
            await session.commit()

        created = sum(1 for s in results.values() if s == "created")
        skipped = sum(1 for s in results.values() if s == "skipped")
        for name, status in results.items():
            print(f"  {status:8s} {name}")
        print(f"seed_pizzas: {created} created, {skipped} skipped")
    finally:
        await engine.dispose()


def main() -> None:
    asyncio.run(_main_async())


if __name__ == "__main__":
    main()
