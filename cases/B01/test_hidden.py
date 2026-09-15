from solution import invoice_total
from decimal import getcontext

def test_per_line_regression():
    assert invoice_total([("0.005", 1), ("0.005", 1)]) == "0.02"

def test_no_rounding_carry_between_lines():
    assert invoice_total([("0.004", 1), ("0.004", 1)]) == "0.00"

def test_zero_quantity():
    assert invoice_total([("999.999999", 0), ("0", 1000)]) == "0.00"

def test_maximum_total():
    assert invoice_total([("1000000", 1000)] * 100) == "100000000000.00"

def test_decimal_precision_boundary():
    assert invoice_total([("2.674999", 1), ("2.675000", 1)]) == "5.35"

def test_input_and_context_unchanged():
    lines = [("1.234", 2), ("5.005", 1)]
    before = list(lines)
    ctx = getcontext()
    settings = repr(ctx)
    assert invoice_total(lines) == "7.48"
    assert lines == before
    assert repr(ctx) == settings
