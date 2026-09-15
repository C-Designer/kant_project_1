import pytest
from solution import ProfileService


def test_interleaved():
    s = ProfileService({"a": {"v": "1"}, "b": {"v": "2"}})
    assert [s.get_profile(k) for k in ["a", "b", "a", "b"]] == [{"v": "1"}, {"v": "2"}, {"v": "1"}, {"v": "2"}]


def test_reverse():
    s = ProfileService({"a": {"v": "1"}, "b": {"v": "2"}})
    assert s.get_profile("b") == {"v": "2"}
    assert s.get_profile("a") == {"v": "1"}


def test_exact_ids():
    s = ProfileService({"": {"v": "empty"}, "A": {"v": "upper"}, "a": {"v": "lower"}})
    for key, value in [("", "empty"), ("A", "upper"), ("a", "lower")]:
        assert s.get_profile(key) == {"v": value}


def test_return_copy():
    s = ProfileService({"a": {"v": "old"}})
    s.get_profile("a")["v"] = "new"
    assert s.get_profile("a") == {"v": "old"}


def test_snapshot():
    p = {"a": {"v": "old"}}
    s = ProfileService(p)
    p["a"]["v"] = "new"
    p["b"] = {}
    assert s.get_profile("a") == {"v": "old"}
    with pytest.raises(KeyError):
        s.get_profile("b")


def test_missing():
    s = ProfileService({"a": {"v": "ok"}})
    assert s.get_profile("a") == {"v": "ok"}
    with pytest.raises(KeyError):
        s.get_profile("missing")
    assert s.get_profile("a") == {"v": "ok"}
    with pytest.raises(KeyError):
        ProfileService({}).get_profile("a")


def test_instances():
    s = ProfileService({"a": {"v": "one"}})
    t = ProfileService({"a": {"v": "two"}})
    assert s.get_profile("a") == {"v": "one"}
    assert t.get_profile("a") == {"v": "two"}
