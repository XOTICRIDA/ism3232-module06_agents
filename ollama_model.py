# ollama_model.py
# Author: [River Sookralli]

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