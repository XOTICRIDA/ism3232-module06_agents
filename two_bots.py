# two_bots.py
# two_bots.py
# Author: [River Sookralli]

from chatbot import SupportChatbot
from mock_model import MockModel
from order_tool import OrderLookup
from stock_tool import StockLookup

order_tool = OrderLookup({"A100": "shipped", "A101": "processing"})
stock_tool = StockLookup({"rain jacket": 12, "day pack": 0})

model = MockModel()

sunny = SupportChatbot(
    "Sunny", "You are cheerful and brief.", order_tool, stock_tool, model
)
river = SupportChatbot(
    "River", "You are formal and detailed.", order_tool, stock_tool, model
)

sunny.respond("hello")
sunny.respond("Where is order A100?")
river.respond("hello")

print(sunny.name, len(sunny.history))
print(river.name, len(river.history))
print(sunny.history[1]["content"])
print(river.history[1]["content"])
print(sunny.instructions)
print(river.instructions)
