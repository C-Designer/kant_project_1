from datetime import datetime

def select_window(timestamps: list[datetime], start: datetime, end: datetime) -> list[datetime]:
    for value in [start, end, *timestamps]:
        if value.utcoffset() is None:
            raise ValueError("all timestamps must be timezone-aware")
    if start > end:
        raise ValueError("start must not be after end")
    return [value for value in timestamps if start <= value < end]
