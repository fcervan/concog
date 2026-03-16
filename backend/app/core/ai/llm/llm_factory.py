from backend.app.core.config.settings import LLM_PROVIDER

from .groq_provider import GroqProvider
from .hyperbolic_provider import HyperbolicProvider


def get_llm():

    if LLM_PROVIDER == "groq":
        return GroqProvider()

    if LLM_PROVIDER == "hyperbolic":
        return HyperbolicProvider()

    raise ValueError(f"LLM provider inválido: {LLM_PROVIDER}")