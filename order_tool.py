# order_tool.py
# Author: River Sookralli


class OrderLookup:
    """Manages order status inquiries and modifications."""

    def __init__(self, orders=None):
        self.orders = orders if orders is not None else {}

    def get_order_details(self, order_id: str):
        """Return the status of a given order ID (or None if not found)."""
        clean_id = str(order_id).strip().upper()
        order_data = self.orders.get(clean_id)
        if isinstance(order_data, dict):
            return order_data.get("status")
        return order_data

    def look_up_order(self, order_id: str) -> str:
        """Look up an order and return a formatted status message."""
        clean_id = str(order_id).strip().upper()
        status = self.get_order_details(clean_id)
        if status:
            return f"Order {clean_id} is {status}."
        return f"No order found for ID {clean_id}."

    def find_status(self, order_id: str):
        """Find and return the raw status or None if not found."""
        return self.get_order_details(order_id)

    def change_address(self, order_id: str, new_address: str) -> bool:
        """Update the shipping address for a given order."""
        clean_id = str(order_id).strip().upper()
        if clean_id in self.orders:
            if isinstance(self.orders[clean_id], dict):
                self.orders[clean_id]["address"] = new_address
            else:
                self.orders[clean_id] = {
                    "status": self.orders[clean_id],
                    "address": new_address,
                }
            return True
        return False
