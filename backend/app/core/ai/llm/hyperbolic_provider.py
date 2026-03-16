import requests

from backend.app.core.config.settings import (
    HYPERBOLIC_API_KEY,
    HYPERBOLIC_URL,
    HYPERBOLIC_MODEL
)

from .base_llm import BaseLLM


class HyperbolicProvider(BaseLLM):

    def __init__(self):

        self.api_key = HYPERBOLIC_API_KEY
        self.url = HYPERBOLIC_URL
        self.model = HYPERBOLIC_MODEL

    def generate(self, system_prompt: str, user_prompt: str) -> str:

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.url,
            json=payload,
            headers=headers,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]