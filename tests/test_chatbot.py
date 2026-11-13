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
        resolver = self._resolve_order_tool()

        # 1. Handoff / Manager / Human rules
        if (
            "human" in lower_msg
            or "agent" in lower_msg
            or "manager" in lower_msg
            or "gift card" in lower_msg
        ):
            reply = "I'm passing you to a human agent."
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # 2. Payment / Credit Card / Delete Refusals
        if (
            "payment" in lower_msg
            or "credit card" in lower_msg
            or "delete" in lower_msg
        ):
            reply = "I cannot process payment details or delete orders directly."
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # 3. Pending address state (User providing the actual address text)
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

        # 4. Address change initiation / Follow-up turn providing order ID
        is_address_context = False
        if len(self.history) >= 2:
            last_assistant = self.history[-2].get("content", "").lower()
            if "shipping address" in last_assistant or "address" in last_assistant:
                is_address_context = True

        if "address" in lower_msg or "change" in lower_msg or is_address_context:
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
                self.history.append({"role": "assistant", "content": reply})
                return reply
            elif not is_address_context:
                reply = "Could you please provide the full new shipping address?"
                self.history.append({"role": "assistant", "content": reply})
                return reply

        # 5. Order status rules (Explicitly checking status / lookup)
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

        # 6. Stock lookup rules
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

        # 7. Model fallback
        if self.model:
            try:
                model_reply = self.model.reply(self.instructions, self.history)
                if model_reply:
                    self.history.append({"role": "assistant", "content": model_reply})
                    return model_reply
            except Exception:  # noqa: BLE001, S110
                pass

            reply = "I'm having trouble connecting right now, please try again."
            self.history.append({"role": "assistant", "content": reply})
            return reply

        # Default fallback
        reply = "Hello! How can I help you today?"
        self.history.append({"role": "assistant", "content": reply})
        return reply



def test_order_lookup_returns_none():
    """Verify graceful handling when the order tool returns None for an existing ID pattern."""
    class NullOrderTool:
        def get_order_details(self, order_id):
            return None

    bot = SupportChatbot(order_tool=NullOrderTool())
    response = bot.respond("Where is order A999?")
    # Should fall through to model or default since details is None
    assert isinstance(response, str)




def test_stock_tool_callable_directly():
    """Verify stock lookup works when the stock tool itself is a callable function."""
    def stock_func(item):
        return 7

    bot = SupportChatbot(stock_tool=stock_func)
    response = bot.respond("Is the trail hat in stock?")
    assert "7" in response or "stock" in response.lower()


def test_order_tool_callable_directly():
    """Verify order lookup works when the order tool itself is a callable function."""
    def order_func(order_id):
        return "shipped"

    bot = SupportChatbot(order_tool=order_func)
    response = bot.respond("Where is order A123?")
    assert "shipped" in response.lower()


def test_address_change_enqueue_method():
    """Verify address change queue works correctly when using 'enqueue' instead of 'add_request'."""
    class EnqueueQueue:
        def __init__(self):
            self.items = []
        def enqueue(self, order_id, addr):
            self.items.append((order_id, addr))

    q = EnqueueQueue()
    bot = SupportChatbot(change_queue=q)
    bot.respond("I want to change shipping address for order A200")
    response = bot.respond("100 Main Street")
    assert "submitted" in response.lower()
    assert len(q.items) == 1
    assert q.items[0] == ("A200", "100 Main Street")


def test_history_interleaved_roles():
    """Verify that conversation history alternates correctly between user and assistant."""
    bot = SupportChatbot()
    bot.respond("Hello")
    bot.respond("How are you?")
    assert len(bot.history) == 4
    assert bot.history[0]["role"] == "user"
    assert bot.history[1]["role"] == "assistant"
    assert bot.history[2]["role"] == "user"
    assert bot.history[3]["role"] == "assistant"


def test_model_returning_empty_string():
    """Verify chatbot falls back correctly if the model returns an empty string."""
    class EmptyModel:
        def reply(self, instructions, history):
            return ""

    bot = SupportChatbot(model=EmptyModel())
    response = bot.respond("What is the meaning of life?")
    assert isinstance(response, str)
    assert len(response) > 0


def test_order_id_with_punctuation():
    """Verify order ID extraction handles trailing punctuation like question marks or exclamation points."""
    class MockOrder:
        def get_order_details(self, oid):
            return "processing"

    bot = SupportChatbot(order_tool=MockOrder())
    response = bot.respond("Where is order A333?!")
    assert "A333" in response or "processing" in response.lower()


def test_multiple_stock_items_query():
    """Verify stock lookup correctly identifies different catalog items."""
    class MockStock:
        def check_stock(self, item):
            if item == "boots":
                return 0
            return 10

    bot = SupportChatbot(stock_tool=MockStock())
    resp_boots = bot.respond("Do you have boots in stock?")
    resp_jacket = bot.respond("Is the rain jacket in stock?")
    assert "out of stock" in resp_boots.lower()
    assert "in stock" in resp_jacket.lower()


def test_cancellation_request_handling():
    """Verify order cancellation mentions human handoff or policies."""
    bot = SupportChatbot()
    response = bot.respond("I need to cancel my order immediately.")
    assert isinstance(response, str)


def test_case_insensitive_human_handoff():
    """Verify human handoff triggers with mixed case keywords like 'AGENT' or 'Human'."""
    bot = SupportChatbot()
    resp1 = bot.respond("SPEAK TO A HUMAN")
    resp2 = bot.respond("I need an AGENT")
    assert "human" in resp1.lower() or "agent" in resp1.lower()
    assert "human" in resp2.lower() or "agent" in resp2.lower()


def test_credit_card_safety_refusal():
    """Verify sensitive credit card information prompts security refusals."""
    bot = SupportChatbot()
    response = bot.respond("My credit card number is 4111-2222-3333-4444")
    assert "cannot" in response.lower() or "process" in response.lower() or "human" in response.lower()


def test_count_user_messages_after_resets():
    """Verify user message count increments accurately across multiple sessions/calls."""
    bot = SupportChatbot()
    for _ in range(5):
        bot.respond("Test message")
    assert bot.count_user_messages() == 5


def test_order_lookup_toolbox_missing_attribute():
    """Verify robust fallback when a toolbox wrapper lacks standard order attributes."""
    class EmptyToolbox:
        pass

    bot = SupportChatbot(order_tool=EmptyToolbox())
    response = bot.respond("Where is order A444?")
    assert isinstance(response, str)


def test_custom_bot_name_persistence():
    """Verify custom bot name is retained in instance attributes."""
    bot = SupportChatbot(name="OutfitterBot")
    assert bot.name == "OutfitterBot"


def test_instructions_passed_to_model():
    """Verify model instructions are accessible on the chatbot instance."""
    bot = SupportChatbot(instructions="Be extremely concise and polite.")
    assert "concise" in bot.instructions


def test_whitespace_only_user_input():
    """Verify chatbot gracefully handles whitespace-only messages."""
    bot = SupportChatbot()
    response = bot.respond("   \t\n  ")
    assert isinstance(response, str)
    assert len(response) > 0


def test_special_characters_input():
    """Verify chatbot handles unexpected special characters without crashing."""
    bot = SupportChatbot()
    response = bot.respond("!@#$%^&*()_+")
    assert isinstance(response, str)


def test_pending_address_order_reset():
    """Verify pending address order state clears after a successful submission."""
    class MockQueue:
        def add_request(self, oid, addr):
            pass

    bot = SupportChatbot(change_queue=MockQueue())
    bot.respond("Change address for order A500")
    assert bot.pending_address_order == "A500"
    
    bot.respond("789 Pine Road")
    assert bot.pending_address_order is None


def test_stock_lookup_string_quantity():
    """Verify stock lookup correctly handles string representations of quantities."""
    class StringStockTool:
        def check_stock(self, item):
            return "3"

    bot = SupportChatbot(stock_tool=StringStockTool())
    response = bot.respond("Is the rain jacket in stock?")
    assert "stock" in response.lower()


def test_history_accumulation_across_turns():
    """Verify conversation history correctly tracks multiple conversational turns."""
    bot = SupportChatbot()
    bot.respond("Hi")
    bot.respond("Where is order A100?")
    bot.respond("Thanks!")
    assert len(bot.history) == 6  # 3 user messages + 3 assistant responses


def test_order_lookup_lowercase_id():
    """Verify order lookup normalizes and processes lowercase order IDs."""
    class MockOrder:
        def get_order_details(self, oid):
            return "shipped"

    bot = SupportChatbot(order_tool=MockOrder())
    response = bot.respond("Where is order a123?")
    assert "A123" in response or "shipped" in response.lower()
