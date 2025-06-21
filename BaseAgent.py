api_key= "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"
from openai import OpenAI
import json


class BaseAgent:
    def __init__(self, api_key, model="gpt-4", personality="You are a helpful assistant", pre_prompt="", temperature=0.1):
        """
        Initialize OpenAI connection and settings
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.personality = personality
        self.pre_prompt = pre_prompt  # New section for pre-prompt
        self.temperature = temperature

    def send_prompt(self, query):
        """Send a prompt to OpenAI and get response"""
        messages = [
            {"role": "system", "content": self.personality}
        ]

        if self.pre_prompt:
            messages.append({"role": "system", "content": self.pre_prompt})  # Add pre-prompt as another system message

        messages.append({"role": "user", "content": query})

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        return completion.choices[0].message.content
