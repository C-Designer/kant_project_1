from solution import FakeNotificationService, send_notification


def test_normal():
    s = FakeNotificationService()
    assert send_notification(s, "k", "hello") == "receipt:k"
    assert s.calls == 1
    assert s.effects == [("k", "hello")]


def test_existing_key():
    s = FakeNotificationService()
    assert send_notification(s, "k", "hi") == "receipt:k"
    assert send_notification(s, "k", "hi") == "receipt:k"
    assert s.calls == 2
    assert s.effects == [("k", "hi")]


def test_independent_keys():
    s = FakeNotificationService()
    assert send_notification(s, "", "") == "receipt:"
    assert send_notification(s, "b", "other") == "receipt:b"
    assert s.effects == [("", ""), ("b", "other")]
