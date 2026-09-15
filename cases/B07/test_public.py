from solution import update_profile


def test_name():
    p = {"display_name": "Ada", "bio": "hi", "alerts": True}
    assert update_profile(p, {"display_name": "Bob"}) == {"display_name": "Bob", "bio": "hi", "alerts": True}
    assert p["display_name"] == "Bob"


def test_empty():
    p = {"display_name": "Ada", "bio": None, "alerts": False}
    assert update_profile(p, {}) == p


def test_multiple():
    p = {"display_name": "Ada", "bio": None, "alerts": False}
    patch = {"bio": "hello", "alerts": True}
    assert update_profile(p, patch) == {"display_name": "Ada", "bio": "hello", "alerts": True}
    assert patch == {"bio": "hello", "alerts": True}
