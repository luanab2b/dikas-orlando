# interfaces/agents/agent_interface.py

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

# Este bloco só é lido por verificadores de tipo, evitando importações circulares em tempo de execução
if TYPE_CHECKING:
    from container.clients import ClientContainer
    from container.repositories import RepositoryContainer

class IAgent(ABC):

    @property
    @abstractmethod
    def instructions(self) -> str:
        """As instruções de sistema (system prompt) para o agente."""
        ...

    @property
    @abstractmethod
    def tools(self) -> list:
        """Uma lista com as definições de ferramentas (functions) que o agente pode usar."""
        ...

    @staticmethod
    @abstractmethod
    def factory(client_container: "ClientContainer", repository_container: "RepositoryContainer") -> "IAgent":
        """Um método estático que atua como uma fábrica para criar uma instância do agente."""
        ...
        
    @abstractmethod
    async def execute(self, customer: dict, orchestrator_output: list, context: list) -> str:
        """O principal método de execução do agente."""
        ...