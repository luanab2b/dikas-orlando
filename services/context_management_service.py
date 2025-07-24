# services/context_management_service.py
from interfaces.repositories.context_repository import IConversationContextRepository
from interfaces.repositories.user_repository_interface import IUserRepository
from utils.logger import logger, to_json_dump
from typing import List, Dict, Any, Optional
import json

class ContextManagementService:
    def __init__(
        self,
        context_repository: IConversationContextRepository,
        user_repository: IUserRepository
    ) -> None:
        self.context_repository = context_repository
        self.user_repository = user_repository
    
    async def create_or_update_context(
        self, 
        phone: str, 
        message: str, 
        agent_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict:
        """
        Cria um novo contexto de conversa ou atualiza um existente
        """
        logger.info(f"[CONTEXT MANAGEMENT SERVICE] Processando contexto para o telefone: {phone}")
        
        # Obtém ou cria o usuário
        user = self.user_repository.get_user_by_phone(phone)
        if not user:
            user = self.user_repository.create_user(
                phone=phone,
                name="Novo Usuário"
            )
        
        # Cria um ID de sessão
        session_id = f"session_{phone}"  # Você pode usar um identificador mais elaborado
        
        # Obtém ou cria um contexto para a sessão
        context = self.context_repository.get_latest_context_by_session(session_id)
        
        if not context:
            # Cria um novo contexto se não existir
            logger.info(f"[CONTEXT MANAGEMENT SERVICE] Criando novo contexto para sessão: {session_id}")
            context = self.context_repository.create_context(
                user_id=user.id,
                session_id=session_id,
                agent_id=agent_id
            )
            message_sequence = 0
        else:
            # Conta mensagens existentes para determinar a próxima sequência
            messages = self.context_repository.get_messages_by_context(context.id)
            message_sequence = len(messages)
        
        # Adiciona a mensagem ao contexto
        self.context_repository.add_message(
            context_id=context.id,
            role="user",
            content=message,
            sequence=message_sequence
        )
        
        return {
            "context_id": context.id,
            "user_id": user.id,
            "session_id": session_id,
            "message_sequence": message_sequence,
            "agent_id": agent_id
        }
    
    def save_assistant_response(
        self, 
        context_id: int, 
        content: str, 
        sequence: int,
        function_calls: List[Dict] = None,
        documents: List[Dict] = None
    ) -> Dict:
        """
        Salva a resposta do assistente no contexto
        """
        logger.info(f"[CONTEXT MANAGEMENT SERVICE] Salvando resposta do assistente para contexto: {context_id}")
        
        # Salva a resposta principal
        message = self.context_repository.add_message(
            context_id=context_id,
            role="assistant",
            content=content,
            sequence=sequence
        )
        
        # Salva chamadas de função, se houver
        if function_calls:
            for i, function_call in enumerate(function_calls):
                self.context_repository.add_message(
                    context_id=context_id,
                    role="function_call",
                    content=json.dumps(function_call),
                    sequence=sequence + i + 1,
                    function_call_id=function_call.get("id", f"func_{i}")
                )
        
        # Salva documentos, se houver
        if documents:
            for doc in documents:
                self.context_repository.add_document(
                    context_id=context_id,
                    filename=doc.get("filename", "documento.pdf"),
                    content_type=doc.get("content_type", "application/pdf"),
                    data=doc.get("data"),
                    metadata=doc.get("metadata")
                )
        
        return message.to_dict() if hasattr(message, "to_dict") else message
    
    def get_conversation_history(self, context_id: int) -> List[Dict]:
        """
        Obtém o histórico completo de uma conversa
        """
        logger.info(f"[CONTEXT MANAGEMENT SERVICE] Obtendo histórico de conversa para contexto: {context_id}")
        
        messages = self.context_repository.get_messages_by_context(context_id)
        
        return [message.to_dict() if hasattr(message, "to_dict") else message for message in messages]