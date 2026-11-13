# keyword_model.py
# Author: [River Sookralli]


class KeywordModel:
    """A stand-in model that decides with keyword rules. It needs no AI."""

    def decide(self, instructions, history, tools):
        """Return a reply or a tool request, based on the last message."""
        last = history[-1]
        if last["role"] == "tool":
            return {"text": last["content"]}
        text = last["content"].lower()
        if "order" in text:
            return {"tool": "look_up_order", "arguments": {"order_id": last["content"]}}
        if "stock" in text:
            return {"tool": "check_stock", "arguments": {"item": last["content"]}}
        if "hello" in text:
            return {"text": "Hello! How can I help you today?"}
        return {
            "text": "I'm not sure how to help with that. I can check an order or stock."
        }
