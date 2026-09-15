def validate_options(limit=None, offset=None, include_archived=None) -> dict:
    limit = 20 if limit is None else limit
    offset = 0 if offset is None else offset
    include_archived = False if include_archived is None else include_archived
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer between 1 and 100")
    if type(offset) is not int or offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if type(include_archived) is not bool:
        raise ValueError("include_archived must be a boolean")
    return {"limit": limit, "offset": offset, "include_archived": include_archived}
