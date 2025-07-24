# dikas-orlando/services/context_service.py

import json
from interfaces.repositories.context_repository import IConversationContextRepository
from interfaces.repositories.user_repository_interface import IUserRepository
from typing import Dict, List, Any, Optional
from utils.logger import logger

class ContextService:
    def __init__(
        self,
        context_repository: IConversationContextRepository,
        user_repository: IUserRepository
    ):
        self.context_repository = context_repository
        self.user_repository = user_repository
    
    def store_user_message(self, phone: str, message: str, agent_id: str) -> Dict[str, Any]:
        """Armazena uma mensagem do usuário no contexto"""
        logger.info(f"Armazenando mensagem do usuário com telefone {phone}")
        
        # Obtém ou cria o usuário
        user = self.user_repository.get_user_by_phone(phone)
        if not user:
            user = self.user_repository.create_user(phone=phone, name="Novo Usuário")
        
        # ID de sessão simples
        session_id = f"session_{phone}"
        
        # Obtém ou cria contexto
        context = self.context_repository.get_latest_context_by_session(session_id)
        
        if not context:
            context = self.context_repository.create_context(
                user_id=user.id,
                session_id=session_id,
                agent_id=agent_id
            )
            sequence = 0
        else:
            messages = self.context_repository.get_messages_by_context(context.id)
            sequence = len(messages)
        
        # Armazena a mensagem
        self.context_repository.add_message(
            context_id=context.id,
            role="user",
            content=message,
            sequence=sequence
        )
        
        return {
            "context_id": context.id,
            "user_id": user.id,
            "session_id": session_id,
            "sequence": sequence,
            "agent_id": agent_id
        }
    
    def store_assistant_message(self, context_id: int, message: str, sequence: int) -> Dict[str, Any]:
        """Armazena uma resposta do assistente"""
        logger.info(f"Armazenando resposta do assistente para contexto {context_id}")
        
        message = self.context_repository.add_message(
            context_id=context_id,
            role="assistant",
            content=message,
            sequence=sequence
        )
        
        return message.to_dict() if hasattr(message, "to_dict") else message
    
    def store_function_call(self, context_id: int, function_call: Dict[str, Any], sequence: int) -> Dict[str, Any]:
        """Armazena uma chamada de função"""
        logger.info(f"Armazenando chamada de função para contexto {context_id}")
        
        message = self.context_repository.add_message(
            context_id=context_id,
            role="function_call",
            content=json.dumps(function_call),
            sequence=sequence,
            function_call_id=function_call.get("id", f"func_{sequence}")
        )
        
        return message.to_dict() if hasattr(message, "to_dict") else message
    
    def store_document(self, context_id: int, filename: str, content_type: str, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Armazena um documento"""
        logger.info(f"Armazenando documento {filename} para contexto {context_id}")
        
        document = self.context_repository.add_document(
            context_id=context_id,
            filename=filename,
            content_type=content_type,
            data=data,
            metadata=metadata
        )
        
        return document.to_dict() if hasattr(document, "to_dict") else document
    
    def get_conversation_history(self, phone: str) -> List[Dict[str, Any]]:
        """Obtém o histórico de conversa para um número"""
        # ID de sessão
        session_id = f"session_{phone}"
        
        # Obtém o contexto
        context = self.context_repository.get_latest_context_by_session(session_id)
        if not context:
            return []
        
        # Obtém mensagens
        messages = self.context_repository.get_messages_by_context(context.id)
        
        # Converte para dicionários
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "sequence": msg.sequence,
                "created_at": msg.created_at.isoformat() if hasattr(msg.created_at, 'isoformat') else str(msg.created_at)
            }
            for msg in messages
        ]
    
    def get_documents_by_context_id(self, context_id: int) -> List[Dict[str, Any]]:
        """Obtém documentos de um contexto"""
        documents = self.context_repository.get_documents_by_context(context_id)
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "content_type": doc.content_type,
                "metadata": doc.metadata,
                "created_at": doc.created_at.isoformat() if hasattr(doc.created_at, 'isoformat') else str(doc.created_at)
            }
            for doc in documents
        ]