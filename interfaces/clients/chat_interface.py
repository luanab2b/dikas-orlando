from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class IChat(ABC):
    @abstractmethod
    def send_message(self, phone: str, message: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        pass