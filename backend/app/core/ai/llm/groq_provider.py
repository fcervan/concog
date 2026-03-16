# from groq import Groq

from backend.app.core.config.settings import GROQ_API_KEY, GROQ_MODEL
from langchain_core.prompts import ChatPromptTemplate

from langchain_groq import ChatGroq

from .base_llm import BaseLLM


class GroqProvider(BaseLLM):

    def __init__(self):

        # self.client = Groq(api_key=GROQ_API_KEY)

        self.client = ChatGroq(
            model = 'llama-3.3-70b-versatile',
            temperature = 0.2,
            max_tokens = None,
            timeout = None,
            max_retries = 2
        )

        self.model = GROQ_MODEL

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])

        chain = template | self.client

        res = chain.invoke({"input": user_prompt})

        return res.content