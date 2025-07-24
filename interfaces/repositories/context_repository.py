# interfaces/repositories/conversation_context_repository_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

class IConversationContextRepository(ABC):
    @abstractmethod
    def create_context(self, user_id: int, session_id: str, agent_id: str):
        """Cria um novo contexto de conversa"""
        pass
    
    @abstractmethod
    def get_context_by_id(self, context_id: int):
        """Obtém um contexto pelo ID"""
        pass
    
    @abstractmethod
    def get_latest_context_by_session(self, session_id: str):
        """Obtém o contexto mais recente para uma sessão específica"""
        pass
    
    @abstractmethod
    def get_contexts_by_user(self, user_id: int):
        """Obtém todos os contextos de um usuário específico"""
        pass
    
    @abstractmethod
    def add_message(self, context_id: int, role: str, content: str, sequence: int, function_call_id: Optional[str] = None):
        """Adiciona uma mensagem ao contexto"""
        pass
    
    @abstractmethod
    def get_messages_by_context(self, context_id: int):
        """Obtém todas as mensagens de um contexto específico"""
        pass
    
    @abstractmethod
    def add_document(self, context_id: int, filename: str, content_type: str, data: bytes, metadata: Optional[Dict[str, Any]] = None):
        """Adiciona um documento ao contexto"""
        pass
    
    @abstractmethod
    def get_documents_by_context(self, context_id: int):
        """Obtém todos os documentos de um contexto específico"""
        pass
    
    @abstractmethod
    def delete_context(self, context_id: int) -> bool:
        """Exclui um contexto e todos os seus dados relacionados"""
        pass