from uuid import uuid4

import pytest

from pizzeria.domain.menu_order import InvalidMenuOrder, MenuOrder


def test_rearrange_keeps_the_requested_sequence():
    a, b, c = uuid4(), uuid4(), uuid4()
    order = MenuOrder.rearrange(current=[a, b, c], requested=[c, a, b])
    assert order.pizza_ids == (c, a, b)


def test_rearrange_of_an_empty_menu_is_empty():
    assert MenuOrder.rearrange(current=[], requested=[]).pizza_ids == ()


def test_rearrange_rejects_a_missing_pizza():
    a, b = uuid4(), uuid4()
    with pytest.raises(InvalidMenuOrder):
        MenuOrder.rearrange(current=[a, b], requested=[a])


def test_rearrange_rejects_an_unknown_pizza():
    a, b = uuid4(), uuid4()
    with pytest.raises(InvalidMenuOrder):
        MenuOrder.rearrange(current=[a], requested=[a, b])


def test_rearrange_rejects_a_duplicate_pizza():
    a, b = uuid4(), uuid4()
    with pytest.raises(InvalidMenuOrder):
        MenuOrder.rearrange(current=[a, b], requested=[a, a, b])


def test_invalid_menu_order_is_a_value_error():
    assert issubclass(InvalidMenuOrder, ValueError)
