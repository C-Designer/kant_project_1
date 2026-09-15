from decimal import Decimal, ROUND_HALF_UP, localcontext

def invoice_total(lines: list[tuple[str, int]]) -> str:
    with localcontext():
        total = sum(((Decimal(price) * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) for price, quantity in lines), Decimal("0.00"))
        return format(total, ".2f")
