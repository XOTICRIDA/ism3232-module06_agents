# no_memory.py
# Author: [River Sookralli]

from ollama import chat

MODEL_NAME = "granite4.1:3b"

INSTRUCTIONS = """You are Sunny, a support assistant for Bayside Outfitters.
Answer in one short sentence."""

first = [
    {"role": "system", "content": INSTRUCTIONS},
    {"role": "user", "content": "Hello, my name is Dana."},
]
response = chat(model=MODEL_NAME, messages=first)
print(response.message.content)

second = [
    {"role": "system", "content": INSTRUCTIONS},
    {"role": "user", "content": "What is my name?"},
]
response = chat(model=MODEL_NAME, messages=second)
print(response.message.content)