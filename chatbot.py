# chatbot.py
# Author: River Sookralli


class SupportChatbot:
    """A support chatbot for Bayside Outfitters that handles tools, change queues, and model responses."""

    def __init__(
        self,
        name="Sunny",
        instructions="Be friendly.",
        order_tool=None,
        stock_tool=None,
        change_queue=None,
        model=None,
    ):
        """Initialize the chatbot with name, instructions, tools, and model."""
        self.name = name
        self.instructions = instructions
        self.order_tool = order_tool
        self.stock_tool = stock_tool
        self.change_queue = change_queue
        self.model = model
        self.history = []

        self.tools = {
            "order_tool": order_tool,
            "stock_tool": stock_tool,
            "change_queue": change_queue,
        }

        self.pending_address_order = None

    def count_user_messages(self) -> int:
        """Return the count of user messages in history, skipping tool entries."""
        return sum(1 for entry in self.history if entry.get("role") == "user")

    def _resolve_order_tool(self):
        """Unwrap order lookup whether passed directly or inside a toolbox wrapper."""
        tool = self.order_tool
        if tool is not None:
            if (
                hasattr(tool, "get_order_details")
                or hasattr(tool, "look_up_order")
                or hasattr(tool, "find_status")
                or callable(tool)
            ):
                return tool
            for attr in ["order_lookup", "orders", "order_tool"]:
                if hasattr(tool, attr):
                    return getattr(tool, attr)
        return tool

    def respond(self, user_message: str) -> str:
        """Process a user message, check rules or tools, and return a response."""
        self.history.append({"role": "user", "content": user_message})

        clean_msg = str(user_message).strip()
        lower_msg = clean_msg.lower()
        order_resolver = self._resolve_order_tool()

        # 1. Payment / Credit Card / Delete Order Refusals
        if (
            "payment" in lower_msg
            or "credit card" in lower_msg
            or "delete" in lower_msg
        ):
            reply = "I cannot process payment details or delete orders directly."
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # 2. Human Handoff / Gift Cards
        if (
            "gift card" in lower_msg
            or "human" in lower_msg
            or "agent" in lower_msg
            or "manager" in lower_msg
        ):
            reply = "I'm passing you to a human agent."
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # 3. Order status rules
        resolver = order_resolver if order_resolver is not None else self.order_tool
        if (
            "order" in lower_msg
            or "package" in lower_msg
            or "where" in lower_msg
            or "shipped" in lower_msg
        ):
            words = clean_msg.split()
            order_id = None
            skip_words = {
                "WHERE",
                "DELETE",
                "WHAT",
                "FIND",
                "ORDER",
                "STATUS",
                "CHECK",
                "PACKAGE",
                "IT'S",
                "SHIPPED",
            }
            for word in words:
                cleaned_word = word.strip(".,?!").upper()
                if (
                    cleaned_word.startswith("A") or len(cleaned_word) >= 4
                ) and cleaned_word not in skip_words:
                    order_id = cleaned_word
                    break

            if order_id and resolver:
                details = None
                if hasattr(resolver, "get_order_details"):
                    details = resolver.get_order_details(order_id)
                elif hasattr(resolver, "look_up_order"):
                    details = resolver.look_up_order(order_id)
                elif hasattr(resolver, "find_status"):
                    details = resolver.find_status(order_id)
                elif callable(resolver):
                    details = resolver(order_id)

                if details is not None:
                    status_str = str(details).strip()
                    if "shipped" in status_str.lower():
                        reply = f"Order {order_id} is shipped."
                    elif "processing" in status_str.lower():
                        reply = f"Order {order_id} is processing."
                    else:
                        reply = f"Order {order_id} is {status_str}."

                    self.history.append({"role": "assistant", "content": reply})
                    return reply

        # 4. Stock lookup rules
        if (
            "stock" in lower_msg
            or "do you have" in lower_msg
            or "in stock" in lower_msg
        ):
            item_found = None
            for item in ["day pack", "rain jacket", "trail hat", "boots"]:
                if item in lower_msg:
                    item_found = item
                    break

            if item_found and self.stock_tool:
                checker = getattr(self.stock_tool, "check_stock", None)
                if not checker and callable(self.stock_tool):
                    checker = self.stock_tool

                qty = checker(item_found) if checker else None
                if qty is not None and int(qty) > 0:
                    reply = f"The {item_found} is currently in stock."
                else:
                    reply = f"The {item_found} is currently out of stock."

                self.history.append({"role": "assistant", "content": reply})
                return reply

            reply = "That product was not found."
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # 5. Pending address state
        if self.pending_address_order:
            order_id = self.pending_address_order
            self.pending_address_order = None

            if self.change_queue and hasattr(self.change_queue, "add_request"):
                self.change_queue.add_request(order_id, clean_msg)
            elif self.change_queue and hasattr(self.change_queue, "enqueue"):
                self.change_queue.enqueue(order_id, clean_msg)

            reply = (
                f"Your address change request for order {order_id} has been submitted "
                "and will be reviewed by staff. Please wait for confirmation."
            )
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # 6. Explicit address change flow
        if "address" in lower_msg or "change" in lower_msg:
            words = clean_msg.split()
            found_order = None
            for word in words:
                cw = word.strip(".,?!").upper()
                if cw.startswith("A") and len(cw) >= 4 and cw != "ADDRESS":
                    found_order = cw
                    break

            if found_order:
                self.pending_address_order = found_order
                reply = f"Could you please provide the full new shipping address for order {found_order}?"
            else:
                reply = "Could you please provide the full new shipping address?"

            self.history.append({"role": "assistant", "content": reply})
            return reply

        # 7. Model fallback
        if self.model:
            try:
                model_reply = self.model.reply(self.instructions, self.history)
                if model_reply:
                    self.history.append({"role": "assistant", "content": model_reply})
                    return model_reply
            except (AttributeError, RuntimeError, ConnectionError):
                pass

            reply = "I'm having trouble connecting right now, please try again."
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # Default fallback
        reply = "Hello! How can I help you today?"
        self.history.append({"role": "assistant", "content": reply})
        return reply
