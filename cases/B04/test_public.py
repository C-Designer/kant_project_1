from datetime import datetime
import pytest
from solution import select_window

def dt(text):
    return datetime.fromisoformat(text)

def test_half_open_utc():
    start = dt("2026-01-01T00:00:00+00:00")
    middle = dt("2026-01-01T12:00:00+00:00")
    end = dt("2026-01-02T00:00:00+00:00")
    assert select_window([start, middle, end], start, end) == [start, middle]

def test_empty_input():
    assert select_window([], dt("2026-01-01T00:00:00+00:00"), dt("2026-01-02T00:00:00+00:00")) == []

def test_naive_start():
    with pytest.raises(ValueError) as exc:
        select_window([], dt("2026-01-01"), dt("2026-01-02T00:00:00+00:00"))
    assert str(exc.value) == "all timestamps must be timezone-aware"

def test_reversed_window():
    with pytest.raises(ValueError) as exc:
        select_window([], dt("2026-01-02T00:00:00+00:00"), dt("2026-01-01T00:00:00+00:00"))
    assert str(exc.value) == "start must not be after end"
