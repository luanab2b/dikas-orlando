# interfaces/repositories/conversation_repository_interface.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class IConversationRepository(ABC):
    """
    Interface para repositórios de conversas.
    Define os métodos que qualquer repositório de conversas deve implementar.
    """
    
    @abstractmethod
    def save_history(self, session_id: str, history: List[Dict[str, Any]]) -> bool:
        """
        Salva o histórico de conversas para uma sessão específica.
        
        Args:
            session_id: O ID da sessão
            history: O histórico de conversas
            
        Returns:
            True se o histórico foi salvo com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_history(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        Recupera o histórico de conversas para uma sessão específica.
        
        Args:
            session_id: O ID da sessão
            
        Returns:
            O histórico de conversas se encontrado, None caso contrário
        """
        pass
    
    @abstractmethod
    def clear_history(self, session_id: str) -> bool:
        """
        Limpa o histórico de conversas para uma sessão específica.
        
        Args:
            session_id: O ID da sessão
            
        Returns:
            True se o histórico foi limpo com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def list_sessions(self) -> List[str]:
        """
        Lista todas as sessões de conversa disponíveis.
        
        Returns:
            Uma lista com os IDs de todas as sessões disponíveis
        """
        pass