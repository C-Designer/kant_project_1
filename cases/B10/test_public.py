from solution import place_order


def test_normal():
    stock, orders = {"a": 5}, {}
    assert place_order(stock, orders, "o", {"a": 2}) == {"items": {"a": 2}, "status": "confirmed"}
    assert stock == {"a": 3}
    assert orders == {"o": {"items": {"a": 2}, "status": "confirmed"}}


def test_multiple_and_unrelated():
    stock = {"a": 5, "b": 3, "c": 8}
    orders = {"old": {"items": {"retired": 1}, "status": "confirmed"}}
    place_order(stock, orders, "new", {"a": 2, "b": 1})
    assert stock == {"a": 3, "b": 2, "c": 8}
    assert orders == {"old": {"items": {"retired": 1}, "status": "confirmed"}, "new": {"items": {"a": 2, "b": 1}, "status": "confirmed"}}


def test_exact_stock():
    stock, orders = {"": 2}, {}
    assert place_order(stock, orders, "", {"": 2}) == {"items": {"": 2}, "status": "confirmed"}
    assert stock == {"": 0}
