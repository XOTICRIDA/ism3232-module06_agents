# order_tool.py
# Author: River Sookralli


class OrderLookup:
    """Manages order status inquiries."""

    def __init__(self, orders=None):
        self.orders = orders if orders is not None else {}

    def get_order_details(self, order_id: str):
        """Return the status of a given order ID."""
        clean_id = str(order_id).strip()
        return self.orders.get(clean_id, None)
