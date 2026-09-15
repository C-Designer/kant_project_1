from copy import deepcopy


def place_order(inventory, orders, order_id, items, fail_at=None):
    if order_id in orders:
        raise ValueError("duplicate order")
    for sku, quantity in items.items():
        if sku not in inventory or inventory[sku] < quantity:
            raise ValueError("unavailable stock")
    for sku, quantity in items.items():
        inventory[sku] -= quantity
    if fail_at == "after_stock":
        raise RuntimeError("simulated failure")
    orders[order_id] = {"items": deepcopy(items), "status": "confirmed"}
    if fail_at == "after_order":
        raise RuntimeError("simulated failure")
    return deepcopy(orders[order_id])
