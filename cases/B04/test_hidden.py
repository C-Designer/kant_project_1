from datetime import datetime
import pytest
from solution import select_window

def dt(text):
    return datetime.fromisoformat(text)

def test_offsets_cross_calendar_day():
    start = dt("2026-01-01T00:00:00+09:00")
    end = dt("2026-01-02T00:00:00+09:00")
    values = [dt("2025-12-31T15:00:00+00:00"), dt("2026-01-01T14:59:59+00:00"), dt("2026-01-01T15:00:00+00:00")]
    assert select_window(values, start, end) == values[:2]

def test_negative_offset_and_fractional_boundary():
    start = dt("2026-03-01T00:00:00+00:00")
    end = dt("2026-03-01T01:00:00+00:00")
    values = [dt("2026-02-28T19:00:00-05:00"), dt("2026-02-28T19:59:59.999999-05:00"), dt("2026-02-28T20:00:00-05:00")]
    assert select_window(values, start, end) == values[:2]

def test_equal_instant_window():
    start = dt("2026-01-01T09:00:00+09:00")
    end = dt("2026-01-01T00:00:00+00:00")
    assert select_window([start, end], start, end) == []

def test_preserve_order_duplicates_timezone_and_input():
    start = dt("2026-01-01T00:00:00+00:00")
    end = dt("2026-01-02T00:00:00+00:00")
    later = dt("2026-01-01T23:00:00+05:30")
    earlier = dt("2026-01-01T01:00:00+00:00")
    values = [later, earlier, later]
    result = select_window(values, start, end)
    assert result == values
    assert [v.isoformat() for v in result] == [v.isoformat() for v in values]
    assert result is not values
    result.clear()
    assert values == [later, earlier, later]

def test_naive_end_or_item_even_outside_window():
    start = dt("2026-01-01T00:00:00+00:00")
    end = dt("2026-01-02T00:00:00+00:00")
    for values, upper in (([], dt("2026-01-02")), ([dt("2001-01-01")], end)):
        with pytest.raises(ValueError) as exc:
            select_window(values, start, upper)
        assert str(exc.value) == "all timestamps must be timezone-aware"

def test_validation_priority_and_absolute_reversal():
    start = dt("2026-01-01T02:00:00+00:00")
    end = dt("2026-01-01T10:00:00+09:00")
    with pytest.raises(ValueError) as exc:
        select_window([dt("2026-01-01")], start, end)
    assert str(exc.value) == "all timestamps must be timezone-aware"
    with pytest.raises(ValueError) as exc:
        select_window([], start, end)
    assert str(exc.value) == "start must not be after end"
