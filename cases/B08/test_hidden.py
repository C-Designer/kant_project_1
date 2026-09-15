import pytest
from solution import FakeNotificationService, TransientError, PermanentError, send_notification


def test_before_retry():
    s = FakeNotificationService(["before", "before", "ok"])
    assert send_notification(s, "k", "hi") == "receipt:k"
    assert s.calls == 3
    assert s.effects == [("k", "hi")]


def test_after_dedup():
    s = FakeNotificationService(["after", "after", "ok"])
    assert send_notification(s, "k", "hi") == "receipt:k"
    assert s.calls == 3
    assert s.effects == [("k", "hi")]


def test_permanent_immediate():
    s = FakeNotificationService(["permanent", "ok"])
    with pytest.raises(PermanentError):
        send_notification(s, "k", "hi")
    assert s.calls == 1
    assert s.effects == []


def test_bounded_attempts():
    for limit in (1, 2, 4):
        s = FakeNotificationService(["before"] * 5)
        with pytest.raises(TransientError):
            send_notification(s, "k", "hi", limit)
        assert s.calls == limit
        assert s.effects == []
    s = FakeNotificationService(["after"])
    with pytest.raises(TransientError):
        send_notification(s, "k", "hi", 1)
    assert s.calls == 1
    assert s.effects == [("k", "hi")]


def test_invalid_limit():
    s = FakeNotificationService()
    for limit in (0, -2):
        with pytest.raises(ValueError):
            send_notification(s, "k", "hi", limit)
    assert s.calls == 0
    assert s.effects == []


def test_generic_service_and_exception_identity():
    class Service:
        def __init__(self, outcomes):
            self.outcomes = iter(outcomes)
            self.calls = []
        def send(self, key, message):
            self.calls.append((key, message))
            outcome = next(self.outcomes)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
    s = Service([TransientError("one"), "custom-receipt", "unused"])
    assert send_notification(s, "", "") == "custom-receipt"
    assert s.calls == [("", ""), ("", "")]
    for error in (PermanentError("permanent"), RuntimeError("unexpected")):
        s = Service([error])
        with pytest.raises(type(error)) as caught:
            send_notification(s, "k", "m")
        assert caught.value is error
        assert s.calls == [("k", "m")]
    last = TransientError("last")
    s = Service([TransientError("first"), last])
    with pytest.raises(TransientError) as caught:
        send_notification(s, "k", "m", 2)
    assert caught.value is last
    assert s.calls == [("k", "m"), ("k", "m")]


def test_fake_contract():
    plan = ["after", "before", "permanent", "ok"]
    s = FakeNotificationService(plan)
    plan[0] = "ok"
    with pytest.raises(TransientError):
        s.send("k", "m")
    with pytest.raises(TransientError):
        s.send("k", "m")
    with pytest.raises(PermanentError):
        s.send("k", "m")
    assert s.send("k", "m") == "receipt:k"
    assert s.send("b", "n") == "receipt:b"
    assert s.calls == 5
    assert s.effects == [("k", "m"), ("b", "n")]
    assert plan == ["ok", "before", "permanent", "ok"]
    t = FakeNotificationService(("ok",))
    assert t.send("k", "m") == "receipt:k"
    assert t.calls == 1 and t.effects == [("k", "m")]
