# ollama_model.py
# Author: [ River Sookralli]

from ollama import ResponseError, chat


class OllamaModel:
    """A real AI model that runs on this computer through Ollama."""

    def __init__(self, model_name):
        """Remember which model to ask."""
        self.model_name = model_name

    def reply(self, instructions, history):
        """Send the instructions and the conversation to the model. Return its reply."""
        messages = [{"role": "system", "content": instructions}]
        messages = messages + history
        try:
            response = chat(model=self.model_name, messages=messages)
        except ConnectionError:
            return None
        except ResponseError:
            return None
        return response.message.content

    def decide(self, instructions, history, tools):
        """Send the conversation and the tools. Return a reply or a tool request."""
        messages = [{"role": "system", "content": instructions}]
        for message in history:
            if message["role"] == "tool":
                messages = messages + self.tool_messages(message)
            else:
                messages.append(message)
        try:
            response = chat(model=self.model_name, messages=messages, tools=tools)
        except ConnectionError:
            return None
        except ResponseError:
            return None
        if response.message.tool_calls:
            call = response.message.tool_calls[0]
            return {"tool": call.function.name, "arguments": call.function.arguments}
        return {"text": response.message.content}

    def tool_messages(self, message):
        """Turn one tool entry into the two messages Ollama expects."""
        name = message["tool_name"]
        request = {"function": {"name": name, "arguments": message["arguments"]}}
        return [
            {"role": "assistant", "content": "", "tool_calls": [request]},
            {"role": "tool", "tool_name": name, "content": message["content"]},
        ]
