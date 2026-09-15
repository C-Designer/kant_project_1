from solution import paginate

def test_first_page():
    assert paginate([1, 2, 3, 4], 1, 2) == {"items": [1, 2], "page": 1, "page_size": 2, "total": 4, "total_pages": 2, "has_next": True}

def test_second_page():
    assert paginate([1, 2, 3, 4], 2, 2)["items"] == [3, 4]

def test_partial_last_page():
    result = paginate([1, 2, 3], 2, 2)
    assert result == {"items": [3], "page": 2, "page_size": 2, "total": 3, "total_pages": 2, "has_next": False}

def test_empty():
    assert paginate([], 1, 10) == {"items": [], "page": 1, "page_size": 10, "total": 0, "total_pages": 0, "has_next": False}
