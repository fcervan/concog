from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Executa uma chamada ao modelo LLM.

        system_prompt -> instrução do sistema
        user_prompt   -> prompt do usuário

        retorna texto gerado
        """
        pass