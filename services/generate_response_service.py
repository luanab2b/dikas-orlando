# dikas-orlando/services/generate_response_service.py

import os
import re
import json
from interfaces.clients.chat_interface import IChat
from interfaces.repositories.message_repository_interface import IMessageRepository
from interfaces.orchestrators.response_orchestrator_interface import IResponseOrchestrator
from services.context_service import ContextService  # NOVA IMPORTAÇÃO
from utils.logger import logger, to_json_dump

class GenerateResponseService:
    def __init__(
        self,
        chat_client: IChat,
        message_repository: IMessageRepository,
        response_orchestrator: IResponseOrchestrator,
        context_service: ContextService = None  # NOVO PARÂMETRO OPCIONAL
    ) -> None:
        self.chat = chat_client
        self.message_repository = message_repository
        self.response_orchestrator = response_orchestrator
        self.context_service = context_service  # NOVO ATRIBUTO

    # Mantém os métodos existentes

    # Modifica o método execute
    async def execute(self, phone: str, message: str) -> None:
        # Inicializa informações de contexto
        context_info = None
        if self.context_service:  # Verifica se o serviço de contexto está disponível
            # Armazena a mensagem no sistema de contexto
            context_info = self.context_service.store_user_message(
                phone=phone,
                message=message,
                agent_id="default"  # Temporário, será atualizado
            )
        
        # Código existente para obter mensagens
        messages: list = self.message_repository.get_latest_customer_messages(
            phone=phone, limit=int(os.getenv("CONTEXT_SIZE", 80))
        )

        context: list[dict] = self._prepare_context(
            context=messages or [],
            user_input=message,
        )

        logger.info(
            f"[GENERATE RESPONSE SERVICE] Gerando resposta para o número: {phone}"
        )

        try:
            full_output: list[dict] = await self.response_orchestrator.execute(
                context=context, phone=phone
            )

            resolved_output_content = self._resolve_output_content(full_output)

            self.chat.send_message(
                phone=phone,
                message=resolved_output_content,
            )

            # Armazenar no sistema tradicional
            self._save_messages_to_database(
                phone=phone,
                input=context[-1],
                outputs=full_output,
            )
            
            # Se o serviço de contexto estiver disponível, armazena resposta no novo sistema
            if self.context_service and context_info:
                # Identifica tipos de saídas
                assistant_content = ""
                function_calls = []
                next_sequence = context_info["sequence"] + 1
                
                for output in full_output:
                    # Encontra a resposta do assistente
                    if output.get("role") == "assistant":
                        assistant_content = output.get("content", "")
                        agent_id = output.get("agent_id", "unknown_agent")
                    
                    # Identifica chamadas de função
                    elif output.get("type", "") == "function_call":
                        function_calls.append(output)
                
                # Armazena a resposta
                if assistant_content:
                    self.context_service.store_assistant_message(
                        context_id=context_info["context_id"],
                        message=assistant_content,
                        sequence=next_sequence
                    )
                    next_sequence += 1
                
                # Armazena chamadas de função
                for func_call in function_calls:
                    self.context_service.store_function_call(
                        context_id=context_info["context_id"],
                        function_call=func_call,
                        sequence=next_sequence
                    )
                    next_sequence += 1

            logger.info(
                f"[GENERATE RESPONSE SERVICE] Resposta final: \ninput: {to_json_dump(context[-1])} \noutput: {to_json_dump(resolved_output_content)}"
            )

        except Exception as e:
            logger.exception(
                f"[GENERATE RESPONSE SERVICE] ❌ Erro ao gerar resposta: \n{to_json_dump(e)}"
            )

            raise e