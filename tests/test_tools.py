from change_queue import ChangeQueue
from order_tool import OrderLookup
from stock_tool import StockLookup
from toolbox import Toolbox


def make_tools():
    """Build fresh tools with two orders for each test."""
    orders = {
        "A100": {"status": "shipped", "address": "14 Bay Road"},
        "A101": {"status": "processing", "address": "3 Gull Lane"},
    }
    order_tool = OrderLookup(orders)
    stock_tool = StockLookup({"rain jacket": 12, "day pack": 0})
    return Toolbox(order_tool, stock_tool, ChangeQueue(order_tool))


def customer(text):
    """Build a history that holds one customer message."""
    return [{"role": "user", "content": text}]


def test_look_up_known_order():
    tools = make_tools()
    assert tools.order_tool.look_up_order("A100") == "Order A100 is shipped."


def test_look_up_unknown_order():
    tools = make_tools()
    assert "No order" in tools.order_tool.look_up_order("A999")


def test_check_stock_for_known_and_unknown_products():
    tools = make_tools()
    assert (
        tools.stock_tool.check_stock("day pack")
        == "We have 0 of the day pack in stock."
    )
    assert tools.stock_tool.check_stock("tent") == "That product was not found."


def test_request_waits_and_changes_nothing():
    tools = make_tools()
    tools.change_queue.request_address_change("A100", "9 Pine Street")
    assert tools.change_queue.waiting()[0]["status"] == "waiting"
    assert tools.order_tool.orders["A100"]["address"] == "14 Bay Road"


def test_approve_makes_the_change_once():
    tools = make_tools()
    tools.change_queue.request_address_change("A100", "9 Pine Street")
    assert tools.change_queue.approve(1) == "Request 1 approved."
    assert tools.order_tool.orders["A100"]["address"] == "9 Pine Street"
    assert tools.change_queue.approve(1) == "Request 1 is already approved."


def test_reject_changes_nothing_and_cannot_be_approved_later():
    tools = make_tools()
    tools.change_queue.request_address_change("A100", "9 Pine Street")
    tools.change_queue.reject(1)
    assert tools.change_queue.approve(1) == "Request 1 is already rejected."
    assert tools.order_tool.orders["A100"]["address"] == "14 Bay Road"


def test_approve_unknown_request():
    tools = make_tools()
    assert tools.change_queue.approve(7) == "There is no request 7."


def test_missing_argument_is_refused():
    tools = make_tools()
    reply = tools.run("look_up_order", {}, customer("Where is my order?"))
    assert "missing" in reply


def test_order_id_must_come_from_the_customer():
    tools = make_tools()
    reply = tools.run("look_up_order", {"order_id": "A101"}, customer("Where is A100?"))
    assert "has not given that order ID" in reply


def test_customer_said_ignores_capitals():
    tools = make_tools()
    assert tools.customer_said(customer("Ship it to 9 PINE STREET"), "9 Pine Street")


def test_unknown_order_containing_a_known_id_is_not_queued():
    tools = make_tools()
    reply = tools.change_queue.request_address_change("A1000", "9 Pine Street")
    assert "No order" in reply
    assert tools.change_queue.waiting() == []
