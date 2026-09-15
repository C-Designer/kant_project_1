from copy import deepcopy
import pytest
from solution import place_order


def state():
    return {"a": 4, "b": 5}, {"old": {"items": {"a": 1}, "status": "confirmed"}}


def test_after_stock_rollback():
    stock, orders = state()
    before = deepcopy((stock, orders))
    items = {"a": 2, "b": 3}
    with pytest.raises(RuntimeError):
        place_order(stock, orders, "new", items, "after_stock")
    assert (stock, orders) == before
    assert items == {"a": 2, "b": 3}


def test_after_order_rollback():
    stock, orders = state()
    before = deepcopy((stock, orders))
    items = {"a": 4, "b": 5}
    with pytest.raises(RuntimeError):
        place_order(stock, orders, "new", items, "after_order")
    assert (stock, orders) == before
    assert items == {"a": 4, "b": 5}


def test_failure_then_success():
    for stage in ("after_stock", "after_order"):
        stock, orders = state()
        with pytest.raises(RuntimeError):
            place_order(stock, orders, "new", {"a": 3}, stage)
        assert place_order(stock, orders, "new", {"a": 3}) == {"items": {"a": 3}, "status": "confirmed"}
        assert stock == {"a": 1, "b": 5}
        assert orders == {"old": {"items": {"a": 1}, "status": "confirmed"}, "new": {"items": {"a": 3}, "status": "confirmed"}}


def test_shortage_atomic():
    for stage in (None, "after_stock", "after_order"):
        stock, orders = state()
        before = deepcopy((stock, orders))
        items = {"a": 2, "b": 6}
        with pytest.raises(ValueError):
            place_order(stock, orders, "new", items, stage)
        assert (stock, orders) == before
        assert items == {"a": 2, "b": 6}


def test_missing_sku_atomic():
    stock, orders = state()
    before = deepcopy((stock, orders))
    items = {"a": 1, "A": 1}
    with pytest.raises(ValueError):
        place_order(stock, orders, "new", items, "after_order")
    assert (stock, orders) == before
    assert items == {"a": 1, "A": 1}


def test_duplicate_atomic():
    stock, orders = state()
    before = deepcopy((stock, orders))
    items = {"a": 1}
    with pytest.raises(ValueError):
        place_order(stock, orders, "old", items, "after_stock")
    assert (stock, orders) == before
    assert items == {"a": 1}


def test_copies_and_sequential_success():
    stock, orders = state()
    items = {"a": 1}
    result = place_order(stock, orders, "first", items)
    assert items == {"a": 1}
    result["items"]["a"] = 99
    result["status"] = "changed"
    items["a"] = 88
    place_order(stock, orders, "second", {"a": 2})
    assert stock == {"a": 1, "b": 5}
    assert orders == {"old": {"items": {"a": 1}, "status": "confirmed"}, "first": {"items": {"a": 1}, "status": "confirmed"}, "second": {"items": {"a": 2}, "status": "confirmed"}}
