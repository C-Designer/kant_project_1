import pytest
from solution import IdempotencyStore

def test_same_total_different_payload_conflicts_and_preserves_state():
    store = IdempotencyStore()
    store.execute("k", {"a": 2, "b": 3})
    for payload in ({"a": 3, "b": 2}, {"c": 5}):
        with pytest.raises(ValueError) as exc:
            store.execute("k", payload)
        assert str(exc.value) == "idempotency key reused with different payload"
    assert store.execute("k", {"a": 2, "b": 3}) == {"total": 5}

def test_dict_order_does_not_matter():
    store = IdempotencyStore()
    store.execute("k", {"a": 2, "b": 7})
    assert store.execute("k", {"b": 7, "a": 2}) == {"total": 9}

def test_input_snapshot_and_no_input_mutation():
    store = IdempotencyStore()
    payload = {"a": 4}
    assert store.execute("k", payload) == {"total": 4}
    assert payload == {"a": 4}
    payload["a"] = 8
    assert store.execute("k", {"a": 4}) == {"total": 4}
    with pytest.raises(ValueError) as exc:
        store.execute("k", payload)
    assert str(exc.value) == "idempotency key reused with different payload"
    assert payload == {"a": 8}

def test_return_values_are_independent():
    store = IdempotencyStore()
    first = store.execute("k", {"a": 4})
    first["total"] = 100
    first["extra"] = 9
    second = store.execute("k", {"a": 4})
    assert second == {"total": 4}
    third = store.execute("k", {"a": 4})
    second.clear()
    assert third == {"total": 4}
    assert store.execute("k", {"a": 4}) == {"total": 4}

def test_key_spelling_and_instance_isolation():
    one = IdempotencyStore()
    two = IdempotencyStore()
    assert one.execute("Key", {"x": 1}) == {"total": 1}
    assert one.execute("key", {"x": 2}) == {"total": 2}
    assert one.execute("Key ", {"x": 3}) == {"total": 3}
    assert two.execute("Key", {"x": 9}) == {"total": 9}
    assert one.execute("Key", {"x": 1}) == {"total": 1}

def test_empty_and_negative_payloads():
    store = IdempotencyStore()
    assert store.execute("empty", {}) == {"total": 0}
    assert store.execute("empty", {}) == {"total": 0}
    assert store.execute("refund", {"a": -10, "b": 3}) == {"total": -7}
    assert store.execute("refund", {"b": 3, "a": -10}) == {"total": -7}
