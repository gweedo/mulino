from decimal import Decimal

import pytest

from pizzeria.domain.money import Money


def test_money_creation():
    """Money can be created with amount and currency."""
    m = Money(amount=Decimal("12.50"), currency="EUR")
    assert m.amount == Decimal("12.50")
    assert m.currency == "EUR"


def test_money_amount_must_be_positive():
    """Money amount must be greater than 0."""
    with pytest.raises(ValueError, match="amount must be greater than 0"):
        Money(amount=Decimal("0"), currency="EUR")

    with pytest.raises(ValueError, match="amount must be greater than 0"):
        Money(amount=Decimal("-5"), currency="EUR")


def test_money_currency_must_be_3_chars_uppercase():
    """Currency must be exactly 3 uppercase ISO 4217 characters."""
    with pytest.raises(ValueError, match="currency must be 3 uppercase ISO 4217"):
        Money(amount=Decimal("10"), currency="EU")

    with pytest.raises(ValueError, match="currency must be 3 uppercase ISO 4217"):
        Money(amount=Decimal("10"), currency="EURO")

    with pytest.raises(ValueError, match="currency must be 3 uppercase ISO 4217"):
        Money(amount=Decimal("10"), currency="eur")


def test_money_equality():
    """Two Money objects with same amount and currency are equal."""
    m1 = Money(amount=Decimal("12.50"), currency="EUR")
    m2 = Money(amount=Decimal("12.50"), currency="EUR")
    assert m1 == m2


def test_money_inequality():
    """Money objects with different amount or currency are not equal."""
    m1 = Money(amount=Decimal("12.50"), currency="EUR")
    m2 = Money(amount=Decimal("13.00"), currency="EUR")
    m3 = Money(amount=Decimal("12.50"), currency="USD")
    assert m1 != m2
    assert m1 != m3


def test_money_formatting():
    """Money formats as 'amount currency'."""
    m = Money(amount=Decimal("12.50"), currency="EUR")
    assert str(m) == "12.50 EUR"

    m2 = Money(amount=Decimal("100"), currency="USD")
    assert str(m2) == "100 USD"
