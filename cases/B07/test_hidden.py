import pytest
from solution import update_profile


def profile():
    return {"display_name": "Ada", "bio": "hello", "alerts": True}


def test_null():
    p = profile()
    assert update_profile(p, {"bio": None}) == {"display_name": "Ada", "bio": None, "alerts": True}
    assert p["bio"] is None


def test_false():
    p = profile()
    update_profile(p, {"alerts": False})
    assert p == {"display_name": "Ada", "bio": "hello", "alerts": False}


def test_empty_strings():
    p = profile()
    update_profile(p, {"display_name": "", "bio": ""})
    assert p == {"display_name": "", "bio": "", "alerts": True}


def test_unknown_atomic():
    p = profile()
    patch = {"display_name": "Bob", "unknown": 1}
    with pytest.raises(ValueError):
        update_profile(p, patch)
    assert p == profile()
    assert patch == {"display_name": "Bob", "unknown": 1}


def test_name_null_atomic():
    p = profile()
    with pytest.raises(ValueError):
        update_profile(p, {"bio": "new", "display_name": None})
    assert p == profile()


def test_alerts_null_atomic():
    p = profile()
    with pytest.raises(ValueError):
        update_profile(p, {"display_name": "Bob", "alerts": None})
    assert p == profile()


def test_copy_and_patch():
    p = profile()
    patch = {"bio": None, "alerts": False}
    result = update_profile(p, patch)
    result["display_name"] = "external"
    assert p == {"display_name": "Ada", "bio": None, "alerts": False}
    assert patch == {"bio": None, "alerts": False}
