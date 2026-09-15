def cancel_order(orders, order_id, actor_id, is_admin=False):
    if order_id not in orders:
        raise KeyError(f"Order with id {order_id} does not exist.")
    
    order = orders[order_id]
    
    if order["status"] == "cancelled":
        return dict(order)
    
    if order["owner_id"] == actor_id or is_admin:
        order["status"] = "cancelled"
        return dict(order)
    
    raise PermissionError("You do not have permission to cancel this order.")
