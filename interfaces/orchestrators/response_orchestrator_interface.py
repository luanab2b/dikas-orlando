# interfaces/orchestrators/response_orchestrator_interface.py
from abc import ABC, abstractmethod

class IResponseOrchestrator(ABC):
    @abstractmethod
    async def execute(self, context: list[dict], phone: str) -> list[dict]:
        pass