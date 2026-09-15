from solution import cancel_order


def test_owner():
    orders = {"1": {"owner_id": "a", "status": "pending"}}
    assert cancel_order(orders, "1", "a") == {"owner_id": "a", "status": "cancelled"}
    assert orders["1"]["status"] == "cancelled"


def test_admin():
    orders = {"1": {"owner_id": "a", "status": "pending"}}
    assert cancel_order(orders, "1", "admin", True) == {"owner_id": "a", "status": "cancelled"}


def test_owner_idempotent():
    orders = {"1": {"owner_id": "a", "status": "cancelled"}}
    assert cancel_order(orders, "1", "a") == cancel_order(orders, "1", "a") == orders["1"]
