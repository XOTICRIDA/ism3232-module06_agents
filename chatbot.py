# chatbot.py
# Author: River Sookralli


class SupportChatbot:
    """A support chatbot. Rules handle what must be right. A model handles the rest."""

    def __init__(self, name, instructions, order_tool, stock_tool, model):
        """Set up one chatbot with its own name, instructions, tools, model, and history."""
        self.name = name
        self.instructions = instructions
        self.order_tool = order_tool
        self.stock_tool = stock_tool
        self.model = model
        self.history = []

    def needs_human(self, text: str) -> bool:
        """Check if request requires human handoff."""
        human_keywords = [
            "shipping address",
            "human",
            "agent",
            "person",
            "representative",
            "manager",
        ]
        return any(kw in text for kw in human_keywords)

    def order_reply(self, user_message: str) -> str:
        """Look up order status using order_tool."""
        text = user_message.lower()
        if self.order_tool:
            for order_id in getattr(self.order_tool, "orders", {}):
                if order_id.lower() in text:
                    status = self.order_tool.get_order_details(order_id)
                    return f"Order {order_id} is {status}."
        return "Please provide a valid order ID so I can look it up."

    def stock_reply(self, user_message: str) -> str:
        """Check stock levels using stock_tool."""
        text = user_message.lower()
        if self.stock_tool:
            for item_name in getattr(self.stock_tool, "inventory", {}):
                if item_name in text:
                    qty = self.stock_tool.check_stock(item_name)
                    return f"We have {qty} of the {item_name} in stock."
        return "I couldn't find that item in our inventory."

    def choose_reply(self, user_message: str) -> str:
        """Use a rule when one applies. Otherwise ask the model."""
        text = user_message.lower()
        if self.needs_human(text):
            return "I can't help with that here. I'm passing you to a human agent."
        if "price match" in text:
            return "I do not know if we price match; please ask a human agent for clarification."
        if "order" in text:
            return self.order_reply(user_message)
        if "stock" in text:
            return self.stock_reply(user_message)
        return self.model_reply()

    def model_reply(self) -> str:
        """Ask the model for a reply. Give a safe answer if the model has none."""
        reply = self.model.reply(self.instructions, self.history)
        if reply is None:
            return "Sorry, I can't answer that right now. Please try again in a moment."
        return reply

    def respond(self, user_message: str) -> str:
        """Append user message to history, generate reply, append assistant reply, and return."""
        self.history.append({"role": "user", "content": user_message})
        reply = self.choose_reply(user_message)
        self.history.append({"role": "assistant", "content": reply})
        return reply
