import requests

from backend.app.core.config.settings import GROQ_API_KEY, GROQ_MODEL
from .base_llm import BaseLLM


class GroqProvider(BaseLLM):

    def __init__(self):
        self.api_key = GROQ_API_KEY
        self.model = GROQ_MODEL
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
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

        response = requests.post(
            self.url,
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]
# # from groq import Groq
#
# from backend.app.core.config.settings import GROQ_API_KEY, GROQ_MODEL
# from langchain_core.prompts import ChatPromptTemplate
#
# from langchain_groq import ChatGroq
#
# from .base_llm import BaseLLM
#
#
# class GroqProvider(BaseLLM):
#
#     def __init__(self):
#
#         # self.client = Groq(api_key=GROQ_API_KEY)
#
#         self.client = ChatGroq(
#             model = 'llama-3.3-70b-versatile',
#             temperature = 0.2,
#             max_tokens = None,
#             timeout = None,
#             max_retries = 2
#         )
#
#         self.model = GROQ_MODEL
#
#     def generate(self, system_prompt: str, user_prompt: str) -> str:
#         template = ChatPromptTemplate.from_messages([
#             ("system", system_prompt),
#             ("human", user_prompt)
#         ])
#
#         chain = template | self.client
#
#         res = chain.invoke({"input": user_prompt})
#
#         return res.content