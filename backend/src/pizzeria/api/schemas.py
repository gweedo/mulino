"""Pydantic v2 DTOs for request bodies and response models."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, model_validator


class LoginRequest(BaseModel):
    email: str
    password: str


class MeResponse(BaseModel):
    id: UUID
    email: str


class MoneyOut(BaseModel):
    amount: Decimal
    currency: str


class PizzaOut(BaseModel):
    id: UUID
    name: str
    description: str
    ingredients: list[str]
    allergens: list[str]
    price: MoneyOut
    available: bool


class PizzaIn(BaseModel):
    name: str
    description: str
    ingredients: list[str]
    allergens: list[str]
    price_amount: Decimal
    price_currency: str


class PizzaUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    ingredients: list[str] | None = None
    allergens: list[str] | None = None
    price_amount: Decimal | None = None
    price_currency: str | None = None
    available: bool | None = None

    @model_validator(mode="after")
    def price_fields_together(self) -> PizzaUpdate:
        has_amount = self.price_amount is not None
        has_currency = self.price_currency is not None
        if has_amount != has_currency:
            raise ValueError("price_amount and price_currency must be provided together")
        return self
