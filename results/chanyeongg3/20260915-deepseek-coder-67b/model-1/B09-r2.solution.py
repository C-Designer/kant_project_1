def cancel_order(orders, order_id, actor_id, is_admin=False):
    if order_id not in orders:
        raise KeyError(f"Order with id {order_id} does not exist")
    
    order = orders[order_id]
    
    if (order['owner_id'] == actor_id) or is_admin or (order['status'] == 'cancelled'):
        order['status'] = 'cancelled'
    else:
        raise PermissionError("You do not have permission to cancel this order")
    
    return dict(order)
