def paginate(items: list[int], page: int, page_size: int) -> dict:
    total = len(items)
    total_pages = total // page_size
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "page": page, "page_size": page_size, "total": total, "total_pages": total_pages, "has_next": page < total_pages}
