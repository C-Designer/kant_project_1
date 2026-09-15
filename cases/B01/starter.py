from decimal import Decimal, ROUND_HALF_UP, localcontext

def invoice_total(lines: list[tuple[str, int]]) -> str:
    with localcontext():
        total = sum((Decimal(price) * quantity for price, quantity in lines), Decimal("0"))
        return format(total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f")
