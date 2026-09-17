from decimal import Decimal, ROUND_HALF_UP


def invoice_total(lines: list[tuple[str, int]]) -> str:
    total = Decimal("0")
    cent = Decimal("0.01")

    for price, quantity in lines:
        line_total = (Decimal(price) * quantity).quantize(
            cent, rounding=ROUND_HALF_UP
        )
        total += line_total

    return format(total, ".2f")
