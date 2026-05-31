"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from pizzeria.api.limiter import limiter
from pizzeria.application.errors import DuplicatePizzaName, InvalidCredentials, PizzaNotFound


async def _json_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse({"detail": f"Rate limit exceeded: {exc.detail}"}, status_code=429)


async def _pizza_not_found_handler(request: Request, exc: PizzaNotFound) -> JSONResponse:
    return JSONResponse({"detail": "Pizza not found"}, status_code=404)


async def _duplicate_pizza_handler(request: Request, exc: DuplicatePizzaName) -> JSONResponse:
    return JSONResponse({"detail": "A pizza with this name already exists"}, status_code=409)


async def _invalid_credentials_handler(
    request: Request, exc: InvalidCredentials
) -> JSONResponse:
    return JSONResponse({"detail": "Invalid email or password"}, status_code=401)


async def _value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=422)


def create_app() -> FastAPI:
    from pizzeria.api.routers.auth import router as auth_router
    from pizzeria.api.routers.pizzas import router as pizzas_router

    app = FastAPI(title="Pizzeria API")

    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    app.add_exception_handler(RateLimitExceeded, _json_rate_limit_handler)
    app.add_exception_handler(PizzaNotFound, _pizza_not_found_handler)
    app.add_exception_handler(DuplicatePizzaName, _duplicate_pizza_handler)
    app.add_exception_handler(InvalidCredentials, _invalid_credentials_handler)
    app.add_exception_handler(ValueError, _value_error_handler)

    app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
    app.include_router(pizzas_router, prefix="/api", tags=["pizzas"])

    return app


app = create_app()
