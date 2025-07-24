# interfaces/repositories/message_repository_interface.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union, Optional

class IMessageRepository(ABC):
    """
    Interface para repositórios de mensagens.
    Define os métodos que qualquer repositório de mensagens deve implementar.
    """
    
    @abstractmethod
    def all(self) -> list:
        """
        Obtém todas as mensagens.
        
        Returns:
            Uma lista com todas as mensagens
        """
        pass
    
    @abstractmethod
    def get_latest_customer_messages(
        self, phone: Optional[Union[int, str]] = None, limit: int = 20
    ) -> list:
        """
        Obtém as mensagens mais recentes de um cliente específico.
        
        Args:
            phone: O número de telefone do cliente
            limit: O número máximo de mensagens a serem retornadas
            
        Returns:
            Uma lista com as mensagens mais recentes
        """
        pass
    
    @abstractmethod
    def create(self, phone: str, role: str, content: Union[str, list]) -> dict:
        """
        Cria uma nova mensagem.
        
        Args:
            phone: O número de telefone associado à mensagem
            role: O papel da mensagem (user, assistant, etc.)
            content: O conteúdo da mensagem
            
        Returns:
            A mensagem criada
        """
        pass