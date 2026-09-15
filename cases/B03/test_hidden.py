import pytest
from solution import validate_options

def test_invalid_limits():
    for value in (0, -1, 101, True, False, 1.0, "1", "", [], {}):
        with pytest.raises(ValueError) as exc:
            validate_options(limit=value)
        assert str(exc.value) == "limit must be an integer between 1 and 100"

def test_invalid_offsets():
    for value in (True, False, -1, 0.0, "0", "", [], {}):
        with pytest.raises(ValueError) as exc:
            validate_options(offset=value)
        assert str(exc.value) == "offset must be a non-negative integer"

def test_invalid_archive_flags():
    for value in (0, 1, 0.0, "false", "", [], {}):
        with pytest.raises(ValueError) as exc:
            validate_options(include_archived=value)
        assert str(exc.value) == "include_archived must be a boolean"

def test_error_precedence():
    with pytest.raises(ValueError) as exc:
        validate_options(0, -1, "bad")
    assert str(exc.value) == "limit must be an integer between 1 and 100"
    with pytest.raises(ValueError) as exc:
        validate_options(1, -1, "bad")
    assert str(exc.value) == "offset must be a non-negative integer"

def test_valid_boundaries_and_new_results():
    first = validate_options(1, 0, False)
    assert first == {"limit": 1, "offset": 0, "include_archived": False}
    first["limit"] = 99
    assert validate_options(1, 0, False)["limit"] == 1
    assert validate_options(100, 10**30, True)["offset"] == 10**30
    assert validate_options(None, 42, True) == {"limit": 20, "offset": 42, "include_archived": True}
    assert validate_options(100, None, True) == {"limit": 100, "offset": 0, "include_archived": True}
    assert validate_options(100, 42, None) == {"limit": 100, "offset": 42, "include_archived": False}
    defaults = validate_options()
    defaults["limit"] = 99
    fresh = validate_options()
    assert fresh == {"limit": 20, "offset": 0, "include_archived": False}
    assert fresh is not defaults

def test_mutable_invalid_input_unchanged():
    value = {"x": [1]}
    with pytest.raises(ValueError) as exc:
        validate_options(offset=value)
    assert str(exc.value) == "offset must be a non-negative integer"
    assert value == {"x": [1]}
