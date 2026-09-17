def validate_options(limit=None, offset=None, include_archived=None) -> dict:
    if limit is None:
        limit = 20
    if offset is None:
        offset = 0
    if include_archived is None:
        include_archived = False

    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("limit must be an integer between 1 and 100")

    if isinstance(offset, bool) or not isinstance(offset, int) or offset < 0:
        raise ValueError("offset must be a non-negative integer")

    if not isinstance(include_archived, bool):
        raise ValueError("include_archived must be a boolean")

    return {
        "limit": limit,
        "offset": offset,
        "include_archived": include_archived,
    }
