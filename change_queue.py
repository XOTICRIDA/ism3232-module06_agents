# change_queue.py
# Author: [River Sookralli]


class ChangeQueue:
    """Changes waiting for a person to approve. Nothing changes until they do."""

    def __init__(self, order_tool):
        """Start with no requests. Approved changes go through the order tool."""
        self.order_tool = order_tool
        self.requests = []

    def request_address_change(self, order_id, new_address):
        """Ask staff to change the shipping address on one order. Staff must approve it.

        Args:
            order_id: The order ID, like A100.
            new_address: The full new shipping address.
        """
        order_id = order_id.upper()
        if self.order_tool.find_status(order_id) is None:
            return "No order with that ID was found. Order IDs look like A100."
        number = len(self.requests) + 1
        request = {
            "number": number,
            "order_id": order_id,
            "new_address": new_address,
            "status": "waiting",
        }
        self.requests.append(request)
        return f"Request {number} was sent to staff. The address has not changed yet."

    def waiting(self):
        """Return the requests that are still waiting for a decision."""
        result = []
        for request in self.requests:
            if request["status"] == "waiting":
                result.append(request)
        return result

    def find(self, number):
        """Return the request with this number, or None."""
        for request in self.requests:
            if request["number"] == number:
                return request
        return None

    def approve(self, number):
        """Approve one waiting request and make the change."""
        request = self.find(number)
        if request is None:
            return f"There is no request {number}."
        if request["status"] != "waiting":
            return f"Request {number} is already {request['status']}."
        request["status"] = "approved"
        self.order_tool.change_address(request["order_id"], request["new_address"])
        return f"Request {number} approved."

    def reject(self, number):
        """Reject one waiting request. Nothing changes."""
        request = self.find(number)
        if request is None:
            return f"There is no request {number}."
        if request["status"] != "waiting":
            return f"Request {number} is already {request['status']}."
        request["status"] = "rejected"
        return f"Request {number} rejected."
