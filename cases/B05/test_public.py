import pytest
from solution import IdempotencyStore

def test_first_request():
    assert IdempotencyStore().execute("order-1", {"item": 120, "fee": 5}) == {"total": 125}

def test_identical_retry():
    store = IdempotencyStore()
    assert store.execute("k", {"a": 3}) == {"total": 3}
    assert store.execute("k", {"a": 3}) == {"total": 3}

def test_distinct_keys():
    store = IdempotencyStore()
    assert store.execute("a", {"x": 1}) == {"total": 1}
    assert store.execute("b", {"x": 2}) == {"total": 2}

def test_changed_payload_conflict():
    store = IdempotencyStore()
    store.execute("k", {"a": 1})
    with pytest.raises(ValueError) as exc:
        store.execute("k", {"a": 2})
    assert str(exc.value) == "idempotency key reused with different payload"
