from solution import paginate

def test_next_partial_page_regression():
    result = paginate([4, 5, 6], 1, 2)
    assert result["total_pages"] == 2
    assert result["has_next"] is True

def test_oversized_page_size():
    result = paginate([9], 1, 100)
    assert result["items"] == [9]
    assert result["total_pages"] == 1
    assert result["has_next"] is False

def test_beyond_end_preserves_request():
    result = paginate([1, 2, 3], 20, 2)
    assert result == {"items": [], "page": 20, "page_size": 2, "total": 3, "total_pages": 2, "has_next": False}

def test_unit_pages():
    result = paginate([8, 7, 6], 2, 1)
    assert result["items"] == [7]
    assert result["total_pages"] == 3
    assert result["has_next"] is True

def test_order_duplicates_and_mutability():
    source = [3, 1, 3]
    result = paginate(source, 1, 10)
    assert source == [3, 1, 3]
    assert result["items"] == source
    result["items"].append(99)
    assert source == [3, 1, 3]
    source[0] = 8
    assert result["items"] == [3, 1, 3, 99]

def test_exact_last_page():
    result = paginate([1, 2, 3, 4], 2, 2)
    assert result["total_pages"] == 2
    assert result["has_next"] is False
