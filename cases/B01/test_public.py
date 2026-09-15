from solution import invoice_total

def test_empty():
    assert invoice_total([]) == "0.00"

def test_integer_prices():
    assert invoice_total([("12", 2), ("3.5", 1)]) == "27.50"

def test_half_up():
    assert invoice_total([("1.005", 1)]) == "1.01"

def test_quantity_before_rounding():
    assert invoice_total([("0.004", 3)]) == "0.01"
