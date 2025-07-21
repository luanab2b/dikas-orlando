# interfaces/orchestrators/response_orchestrator_interface.py
from abc import ABC, abstractmethod
from typing import Coroutine, Any

class IResponseOrchestrator(ABC):
    """
    Define o contrato para qualquer orquestrador de respostas no sistema.
    """
    @abstractmethod
    async def execute(self, context: list[dict], phone: str) -> Coroutine[Any, Any, list[dict] | str]:
        """
        Executa a lógica de orquestração e retorna a resposta do agente apropriado.
        A anotação de retorno Coroutine é uma forma mais explícita para tipagem de funções async.
        """
        pass