from copy import deepcopy

def place_order(inventory, orders, order_id, items, fail_at=None):
    if order_id in orders:
        raise ValueError("duplicate order")
    for sku, quantity in items.items():
        if sku not in inventory or inventory[sku] < quantity:
            raise ValueError("unavailable stock")
    if fail_at == "after_stock":
        raise RuntimeError("simulated failure")
    for sku, quantity in items.items():
        inventory[sku] -= quantity
        if inventory[sku] == 0:
            del inventory[sku]
    orders[order_id] = {"items": dict(items), "status": "confirmed"}
    if fail_at == "after_order":
        raise RuntimeError("simulated failure")
    return deepcopy(orders[order_id])
