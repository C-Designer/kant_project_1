from copy import deepcopy


def place_order(inventory, orders, order_id, items, fail_at=None):
    if order_id in orders:
        raise ValueError("duplicate order")

    for sku, quantity in items.items():
        if sku not in inventory or inventory[sku] < quantity:
            raise ValueError("unavailable stock")

    added_order = False
    try:
        for sku, quantity in items.items():
            inventory[sku] -= quantity

        if fail_at == "after_stock":
            raise RuntimeError("simulated failure")

        orders[order_id] = {
            "items": dict(items),
            "status": "confirmed",
        }
        added_order = True

        if fail_at == "after_order":
            raise RuntimeError("simulated failure")

        return deepcopy(orders[order_id])
    except BaseException:
        if added_order:
            del orders[order_id]
        for sku, quantity in items.items():
            inventory[sku] += quantity
        raise
