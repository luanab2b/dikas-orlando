from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from typing import Any

class IDatabase(ABC):
    @abstractmethod
    def get_session(self) -> AbstractContextManager[Any]:
        pass
    
    @abstractmethod
    def close(self) -> None:
        pass