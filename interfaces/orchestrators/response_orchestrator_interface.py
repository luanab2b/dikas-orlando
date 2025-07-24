from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IResponseOrchestrator(ABC):
    @abstractmethod
    async def execute(self, context: List[Dict[str, Any]], phone: str) -> List[Dict[str, Any]]:
        pass