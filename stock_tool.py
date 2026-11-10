# stock_tool.py
# Author: River Sookralli


class StockLookup:
    """Manages inventory stock level checks."""

    def __init__(self, inventory=None):
        self.inventory = inventory if inventory is not None else {}

    def check_stock(self, item_name: str):
        """Return stock quantity for an item."""
        clean_name = str(item_name).strip().lower()
        for key, val in self.inventory.items():
            if key in clean_name or clean_name in key:
                return val
        return None
