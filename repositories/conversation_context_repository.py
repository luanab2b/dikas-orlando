# repositories/conversation_context_repository.py
from interfaces.repositories.context_repository import IConversationContextRepository
from interfaces.clients.database_interface import IDatabase
from typing import List, Optional, Dict, Any
from database.models.conversation_context import ConversationContext
from database.models.context_message import ContextMessage
from database.models.context_document import ContextDocument

class ConversationContextRepository(IConversationContextRepository):
    def __init__(self, database_client: IDatabase):
        self.db = database_client
    
    def create_context(self, user_id: int, session_id: str, agent_id: str):
        """Cria um novo contexto de conversa"""
        with self.db.get_session() as session:
            context = ConversationContext(
                user_id=user_id,
                session_id=session_id,
                agent_id=agent_id
            )
            session.add(context)
            session.commit()
            session.refresh(context)
            return context
    
    def get_context_by_id(self, context_id: int):
        """Obtém um contexto pelo ID"""
        with self.db.get_session() as session:
            return session.query(ConversationContext).filter(
                ConversationContext.id == context_id
            ).first()
    
    def get_latest_context_by_session(self, session_id: str):
        """Obtém o contexto mais recente para uma sessão específica"""
        with self.db.get_session() as session:
            return session.query(ConversationContext).filter(
                ConversationContext.session_id == session_id
            ).order_by(ConversationContext.created_at.desc()).first()
    
    def get_contexts_by_user(self, user_id: int):
        """Obtém todos os contextos de um usuário específico"""
        with self.db.get_session() as session:
            return session.query(ConversationContext).filter(
                ConversationContext.user_id == user_id
            ).order_by(ConversationContext.created_at.desc()).all()
    
    def add_message(self, 
                   context_id: int, 
                   role: str, 
                   content: str, 
                   sequence: int, 
                   function_call_id: Optional[str] = None):
        """Adiciona uma mensagem ao contexto"""
        with self.db.get_session() as session:
            message = ContextMessage(
                context_id=context_id,
                role=role,
                content=content,
                function_call_id=function_call_id,
                sequence=sequence
            )
            session.add(message)
            session.commit()
            session.refresh(message)
            return message
    
    def get_messages_by_context(self, context_id: int):
        """Obtém todas as mensagens de um contexto específico"""
        with self.db.get_session() as session:
            return session.query(ContextMessage).filter(
                ContextMessage.context_id == context_id
            ).order_by(ContextMessage.sequence).all()
    
    def add_document(self, 
                    context_id: int, 
                    filename: str, 
                    content_type: str, 
                    data: bytes, 
                    metadata: Optional[Dict[str, Any]] = None):
        """Adiciona um documento ao contexto"""
        with self.db.get_session() as session:
            document = ContextDocument(
                context_id=context_id,
                filename=filename,
                content_type=content_type,
                data=data,
                metadata=metadata
            )
            session.add(document)
            session.commit()
            session.refresh(document)
            return document
    
    def get_documents_by_context(self, context_id: int):
        """Obtém todos os documentos de um contexto específico"""
        with self.db.get_session() as session:
            return session.query(ContextDocument).filter(
                ContextDocument.context_id == context_id
            ).all()
    
    def delete_context(self, context_id: int) -> bool:
        """Exclui um contexto e todos os seus dados relacionados"""
        with self.db.get_session() as session:
            context = session.query(ConversationContext).filter(
                ConversationContext.id == context_id
            ).first()
            if not context:
                return False
            
            session.delete(context)
            session.commit()
            return True