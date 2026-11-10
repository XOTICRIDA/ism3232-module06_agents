# Week 11 Answers

## Exercise 1
1. **The message the customer never saw:** System instructions (`{"role": "system", "content": "You are Sunny. Answer in one short sentence."}`)
2. **How many times the customer has spoken:** 2 times (the messages with the role `"user"`).
3. **Can the model tell that the last reply came from the order tool? Why does that matter?** No, the model cannot tell because tool responses are recorded under the `"assistant"` role alongside regular model generated text. This matters because the LLM treats all prior assistant turns as part of its own generated context window rather than as external data retrieved from a deterministic tool.
4. **The customer now types "thanks". How many messages are sent on the next call?** 6 messages will be sent (1 system message, 2 prior user messages, 2 prior assistant messages, and 1 new user message).

---

## Exercise 2
*Implemented in `echo_model.py` and validated through unit tests in `tests/test_chatbot.py`.*

---

## Exercise 3

### Conversation Log
```text
Type a message, or type quit to stop.
You: How long does shipping take?
Sunny: Shipping takes 3 to 5 business days.
You: Can I return a sale item?
Sunny: Sale items cannot be returned.
You: Do you offer gift wrapping?
Sunny: I do not know if we offer gift wrapping, but I can pass you to a human agent.
You: Do you have a store in Orlando?
Sunny: I do not know if we have a store in Orlando, but I can pass you to a human agent.
You: quit
Messages in this conversation: 8