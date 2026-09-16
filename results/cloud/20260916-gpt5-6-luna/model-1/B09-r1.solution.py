def cancel_order(orders: dict[str, dict], order_id: str, actor_id: str, is_admin: bool = False) -> dict:
    order = orders[order_id]

    if not is_admin and order["owner_id"] != actor_id:
        raise PermissionError("actor is not authorized to cancel this order")

    order["status"] = "cancelled"
    return dict(order)
