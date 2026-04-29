import json

import requests

from backend.app.core.config.settings import GROQ_API_KEY, GROQ_MODEL
from .base_llm import BaseLLM


class GroqProvider(BaseLLM):

    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2
            }

            # print(json.dumps(payload))

            response = requests.post(
                self.url,
                headers=headers,
                json=payload,
                timeout=300
            )

            response.raise_for_status()

            data = response.json()

            print(data)

            return data["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"ERRO EXCEPTION: {e}")
            return ""