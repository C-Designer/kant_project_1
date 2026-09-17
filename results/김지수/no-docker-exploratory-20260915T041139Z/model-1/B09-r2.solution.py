def cancel_order(orders, order_id, actor_id, is_admin=False):
    if order_id not in orders:
        raise KeyError("Order ID not found")
    
    order = orders[order_id]
    if order["status"] == "cancelled":
        return dict(order)
    
    if order["owner_id"] == actor_id or is_admin:
        order["status"] = "cancelled"
        return dict(order)
    else:
        raise PermissionError("Permission denied")
