def validate_options(limit=None, offset=None, include_archived=None) -> dict:
    limit = limit if limit is not None else 20
    offset = offset if offset is not None else 0
    include_archived = include_archived if include_archived is not None else False
    if limit is not None and not isinstance(limit, int) or (limit is not None and not 1 <= limit <= 100):
        raise ValueError("limit must be an integer between 1 and 100")
    if offset is not None and not isinstance(offset, int) or (offset is not None and offset < 0):
        raise ValueError("offset must be a non-negative integer")
    if include_archived is not None and not isinstance(include_archived, bool):
        raise ValueError("include_archived must be a boolean")
    return {"limit": limit, "offset": offset, "include_archived": include_archived}
