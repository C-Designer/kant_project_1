import pytest
from solution import validate_options

def test_defaults():
    assert validate_options() == {"limit": 20, "offset": 0, "include_archived": False}

def test_explicit_values():
    assert validate_options(100, 42, True) == {"limit": 100, "offset": 42, "include_archived": True}

def test_none_defaults():
    assert validate_options(None, None, None) == validate_options()

def test_negative_offset():
    with pytest.raises(ValueError) as exc:
        validate_options(offset=-1)
    assert str(exc.value) == "offset must be a non-negative integer"
