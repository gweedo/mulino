"""Pizzas router — public and admin endpoints."""

from uuid import UUID

from fastapi import APIRouter, status

from pizzeria.api.deps import CurrentOwner, PizzaRepoDep
from pizzeria.api.schemas import PizzaIn, PizzaOut, PizzaUpdate
from pizzeria.application.use_cases.create_pizza import CreatePizza
from pizzeria.application.use_cases.delete_pizza import DeletePizza
from pizzeria.application.use_cases.get_pizza import GetPizza
from pizzeria.application.use_cases.list_pizzas import ListPizzas
from pizzeria.application.use_cases.update_pizza import UpdatePizza

router = APIRouter()


def _to_pizza_out(pizza) -> PizzaOut:  # type: ignore[no-untyped-def]
    return PizzaOut(
        id=pizza.id,
        name=pizza.name,
        description=pizza.description,
        ingredients=pizza.ingredients,
        allergens=sorted(a.value for a in pizza.allergens),
        price={"amount": pizza.price.amount, "currency": pizza.price.currency},
        available=pizza.available,
    )


# ── Public endpoints ────────────────────────────────────────────────────────


@router.get("/pizzas", response_model=list[PizzaOut])
async def list_pizzas(repo: PizzaRepoDep) -> list[PizzaOut]:
    pizzas = await ListPizzas(repo).execute(only_available=True)
    return [_to_pizza_out(p) for p in pizzas]


@router.get("/pizzas/{pizza_id}", response_model=PizzaOut)
async def get_pizza(pizza_id: UUID, repo: PizzaRepoDep) -> PizzaOut:
    pizza = await GetPizza(repo).execute(pizza_id, only_available=True)
    return _to_pizza_out(pizza)


# ── Admin endpoints ─────────────────────────────────────────────────────────


@router.get("/admin/pizzas", response_model=list[PizzaOut])
async def admin_list_pizzas(_owner: CurrentOwner, repo: PizzaRepoDep) -> list[PizzaOut]:
    pizzas = await ListPizzas(repo).execute(only_available=False)
    return [_to_pizza_out(p) for p in pizzas]


@router.post("/pizzas", response_model=PizzaOut, status_code=status.HTTP_201_CREATED)
async def create_pizza(
    body: PizzaIn, _owner: CurrentOwner, repo: PizzaRepoDep
) -> PizzaOut:
    pizza = await CreatePizza(repo).execute(
        body.name,
        body.description,
        body.ingredients,
        body.allergens,
        body.price_amount,
        body.price_currency,
    )
    return _to_pizza_out(pizza)


@router.put("/pizzas/{pizza_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_pizza(
    pizza_id: UUID, body: PizzaUpdate, _owner: CurrentOwner, repo: PizzaRepoDep
) -> None:
    await UpdatePizza(repo).execute(
        pizza_id,
        name=body.name,
        description=body.description,
        ingredients=body.ingredients,
        allergen_names=body.allergens,
        price_amount=body.price_amount,
        price_currency=body.price_currency,
        available=body.available,
    )


@router.delete("/pizzas/{pizza_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_pizza(pizza_id: UUID, _owner: CurrentOwner, repo: PizzaRepoDep) -> None:
    await DeletePizza(repo).execute(pizza_id)
