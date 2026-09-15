from solution import ProfileService


def test_single():
    assert ProfileService({"a": {"name": "Ada"}}).get_profile("a") == {"name": "Ada"}


def test_repeat():
    s = ProfileService({"a": {"v": "1"}})
    assert s.get_profile("a") == s.get_profile("a") == {"v": "1"}


def test_empty_profile():
    assert ProfileService({"a": {}}).get_profile("a") == {}
