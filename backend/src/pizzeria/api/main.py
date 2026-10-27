"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from pizzeria.application.errors import DuplicatePizzaName, PizzaNotFound


async def _pizza_not_found_handler(request: Request, exc: PizzaNotFound) -> JSONResponse:
    return JSONResponse({"detail": "Pizza not found"}, status_code=404)


async def _duplicate_pizza_handler(request: Request, exc: DuplicatePizzaName) -> JSONResponse:
    return JSONResponse({"detail": "A pizza with this name already exists"}, status_code=409)


async def _value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=422)


def create_app() -> FastAPI:
    from pizzeria.api.routers.pizzas import router as pizzas_router

    app = FastAPI(title="Pizzeria API")

    app.add_exception_handler(PizzaNotFound, _pizza_not_found_handler)
    app.add_exception_handler(DuplicatePizzaName, _duplicate_pizza_handler)
    app.add_exception_handler(ValueError, _value_error_handler)

    app.include_router(pizzas_router, prefix="/api", tags=["pizzas"])

    return app


app = create_app()
