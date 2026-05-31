"""Unit tests for API Pydantic schemas."""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from pizzeria.api.schemas import PizzaUpdate


def test_pizza_update_price_amount_without_currency_raises():
    with pytest.raises(ValidationError):
        PizzaUpdate(price_amount=Decimal("10"))


def test_pizza_update_price_currency_without_amount_raises():
    with pytest.raises(ValidationError):
        PizzaUpdate(price_currency="EUR")
