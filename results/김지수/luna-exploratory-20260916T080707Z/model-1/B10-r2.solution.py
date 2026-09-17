from copy import deepcopy


def place_order(inventory, orders, order_id, items, fail_at=None):
    if order_id in orders:
        raise ValueError("duplicate order")

    for sku, quantity in items.items():
        if sku not in inventory or inventory[sku] < quantity:
            raise ValueError("unavailable stock")

    original_inventory = inventory.copy()
    had_order = order_id in orders
    original_order = deepcopy(orders[order_id]) if had_order else None

    try:
        for sku, quantity in items.items():
            inventory[sku] -= quantity

        if fail_at == "after_stock":
            raise RuntimeError("simulated failure")

        orders[order_id] = {
            "items": dict(items),
            "status": "confirmed",
        }

        if fail_at == "after_order":
            raise RuntimeError("simulated failure")

        return deepcopy(orders[order_id])
    except Exception:
        inventory.clear()
        inventory.update(original_inventory)

        if had_order:
            orders[order_id] = original_order
        else:
            orders.pop(order_id, None)

        raise
