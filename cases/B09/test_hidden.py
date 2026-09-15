from copy import deepcopy
import pytest
from solution import cancel_order


def test_nonowner_unchanged():
    orders = {"1": {"owner_id": "a", "status": "pending"}, "2": {"owner_id": "b", "status": "pending"}}
    before = deepcopy(orders)
    with pytest.raises(PermissionError):
        cancel_order(orders, "1", "b")
    assert orders == before


def test_cancelled_still_private():
    orders = {"1": {"owner_id": "a", "status": "cancelled"}}
    before = deepcopy(orders)
    with pytest.raises(PermissionError):
        cancel_order(orders, "1", "b")
    assert orders == before


def test_missing():
    orders = {"1": {"owner_id": "a", "status": "pending"}}
    before = deepcopy(orders)
    for admin in (False, True):
        with pytest.raises(KeyError):
            cancel_order(orders, "missing", "a", admin)
        assert orders == before


def test_other_orders_preserved():
    orders = {"1": {"owner_id": "a", "status": "pending"}, "2": {"owner_id": "a", "status": "pending"}}
    cancel_order(orders, "1", "a")
    assert orders == {"1": {"owner_id": "a", "status": "cancelled"}, "2": {"owner_id": "a", "status": "pending"}}


def test_return_copy():
    orders = {"1": {"owner_id": "a", "status": "pending"}}
    result = cancel_order(orders, "1", "a")
    result.update(owner_id="b", status="pending")
    assert orders == {"1": {"owner_id": "a", "status": "cancelled"}}


def test_ids_exact():
    orders = {"": {"owner_id": "", "status": "pending"}, "A": {"owner_id": "Owner", "status": "pending"}}
    assert cancel_order(orders, "", "")["status"] == "cancelled"
    before = deepcopy(orders)
    with pytest.raises(PermissionError):
        cancel_order(orders, "A", "owner", False)
    assert orders == before


def test_admin_cancelled():
    orders = {"1": {"owner_id": "a", "status": "cancelled"}}
    assert cancel_order(orders, "1", "other", True) == {"owner_id": "a", "status": "cancelled"}
