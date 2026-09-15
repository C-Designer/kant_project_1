def cancel_order(orders, order_id, actor_id, is_admin=False):
    order = orders[order_id]
    order["status"] = "cancelled"
    return dict(order)
