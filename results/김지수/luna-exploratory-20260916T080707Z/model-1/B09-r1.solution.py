def cancel_order(orders, order_id, actor_id, is_admin=False):
    order = orders[order_id]

    if not is_admin and order["owner_id"] != actor_id:
        raise PermissionError("actor is not authorized to cancel this order")

    order["status"] = "cancelled"
    return dict(order)
