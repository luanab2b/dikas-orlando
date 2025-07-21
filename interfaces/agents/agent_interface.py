# interfaces/agents/agent_interface.py
from abc import ABC, abstractmethod
from typing import TypedDict, Any

class AgentResponse(TypedDict):
    status: str
    message: str | None
    tool_data: dict[str, Any] | None

class IAgent(ABC):
    @property
    @abstractmethod
    def id(self) -> str: ...

    @property
    @abstractmethod
    def name(self) -> str: ...

    # A assinatura correta e padronizada para todos os agentes
    @abstractmethod
    async def execute(self, context: list[dict], phone: str, user: dict | None) -> AgentResponse:
        """O principal método de execução do agente."""
        ...