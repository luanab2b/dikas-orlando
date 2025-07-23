# agents/roteiro_agent.py
import json
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from interfaces.agents.agent_interface import IAgent, AgentResponse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from container.clients import ClientContainer
    from container.repositories import RepositoryContainer

class RoteiroAgent(IAgent):
    """
    Agente especialista em criar roteiros de viagem para Orlando.
    Este agente segue a estrutura solicitada, mas com a lógica correta
    para se integrar à arquitetura assíncrona e baseada em interfaces.
    """
    # --- Metadados e Configurações do Agente ---
    ID = "#1"
    NAME = "Agente de Roteiro de Viagem"
    MODEL = "gpt-4o-mini"
    TEMPERATURE = 0.5
    MAX_TOKENS = 2048

    def __init__(self, client: AsyncOpenAI):
        """O construtor recebe o cliente da IA já inicializado."""
        self.client = client

    # --- Implementação das Propriedades da Interface ---
    @property
    def id(self) -> str:
        return self.ID

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def instructions(self) -> str:
        """
        Propriedade que retorna as instruções de sistema (system prompt) para a IA.
        """
        return """Você é o "Orlando Trip Planner", uma IA especialista em criar roteiros personalizados para viagens a Orlando (Disney World, Universal, etc.), equilibrando parques, compras, gastronomia e descanso conforme o perfil do usuário.

Seu objetivo é:
- Coletar todas as informações essenciais do viajante, entender estilo, interesses, restrições e logística, e **somente após receber todas as respostas obrigatórias**, montar um roteiro otimizado dia a dia.
- O roteiro deve considerar toques de magia, flexibilidades, logística de transporte/hotel, ritmo do grupo e estimativas realistas.
- Sempre que pedirem contatos de turismo, forneça:
    1. Responsável: Thiago  
    2. Instagram: https://www.instagram.com/melhoresdikasdeorlando/  
    3. WhatsApp: +1 (407) 308-7208
- Persista em obter esclarecimentos até que todos os dados obrigatórios estejam coletados, antes de seguir para o roteiro.
- **Assim que TODAS as informações obrigatórias forem coletadas, acione a function 'roteiro' para gerar o roteiro.**

Regras e formato:
- Idioma padrão: português (Brasil).
- Tom: amigo, claro e objetivo.
- Durante a coleta: faça perguntas em lista numerada.

IMPORTANTE: Só acione a function 'roteiro' após toda a coleta obrigatória. Continue perguntando até que todas as informações sejam fornecidas.

# Output Format
- Durante a coleta: saída em lista numerada das perguntas obrigatórias faltantes.
- Quando todas as respostas foram coletadas: CHAME A FUNCTION 'roteiro' passando todos os dados coletados como argumento. **Não gere o roteiro como texto diretamente, apenas acione a function.**
"""

    @property
    def tools(self) -> list:
        """
        Propriedade que retorna a definição da ferramenta (function) 'roteiro'.
        COLE AQUI A ESTRUTURA EXATA DA SUA FERRAMENTA.
        """
        return [{
            "type": "function",
            "function": {
                "name": "roteiro",
                "description": "Gera um roteiro personalizado para viagem a Orlando com base em informações detalhadas dos viajantes.",
                "parameters": {
                    "type": "object",
                    "required": [
                        "data_chegada", "data_retorno", "dias_completos_orlando", "numero_viajantes", "criancas", "ingressos_parques_comprados", "parques_desejados", "ritmo", "horario_preferido_acordar", "disposicao_fisica", "foco_viagem", "restricoes_alimentares", "reservas_restaurantes_tematicos", "interesse_gastronomico", "cafe_manha_personagens", "preferencia_refeicao", "meio_transporte", "hotel_ou_regiao", "usar_onibus_disney", "programacao_noturna", "passeios_externos", "lojas_prioritarias", "dias_compras_inteligente", "servicos_extras", "dia_livre", "motivo_viagem"
                    ],
                    "properties": {
                        "data_chegada": {"type": "string", "description": "Data de chegada em Orlando, no formato AAAA-MM-DD"},
                        "data_retorno": {"type": "string", "description": "Data de retorno, no formato AAAA-MM-DD"},
                        "dias_completos_orlando": {"type": "integer", "description": "Quantidade de dias completos na cidade"},
                        "numero_viajantes": {"type": "integer", "description": "Número total de viajantes"},
                        "criancas": {"type": "array", "description": "Lista de idades das crianças viajantes...", "items": {"type": "integer"}},
                        "ingressos_parques_comprados": {"type": "boolean", "description": "Se os ingressos já foram comprados"},
                        # ... continue com todas as outras propriedades ...
                        "motivo_viagem": {"type": "string", "description": "Motivo principal da viagem..."}
                    }
                }
            }
        }]

    @staticmethod
    def factory(client_container: "ClientContainer", repository_container: "RepositoryContainer") -> "IAgent":
        """Método fábrica que cria a instância do agente, injetando as dependências corretas."""
        openai_client = client_container.get("async_openai")
        if not openai_client:
            raise ValueError("Cliente 'async_openai' não encontrado.")
        return RoteiroAgent(client=openai_client)

    async def execute(self, context: list[dict], phone: str, user: dict | None) -> AgentResponse:
        """
        Ponto de entrada principal do agente. A assinatura agora é compatível.
        """
        user_name = user['name'] if user and user.get('name') else "Viajante"
        
        # O 'context' recebido já é o histórico completo da conversa
        history = context
        
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.instructions}]

        if len(history) == 1:
            messages.extend([
                {"role": "user", "content": "Olá, quero um roteiro para Orlando."},
                {"role": "assistant", "content": f"Olá, {user_name}! Com certeza! Para criar o roteiro perfeito, preciso de algumas informações..."}
            ]) # type: ignore

        # Adicionando o comentário para instruir o Pylance a ignorar o falso positivo.
        messages.extend(history) # type: ignore
        
        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            temperature=0.5,
            max_tokens=2048
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            return AgentResponse(
                status='tool_call',
                message="Coleta de dados finalizada.",
                tool_data={'name': tool_call.function.name, 'arguments': arguments}
            )
        else:
            return AgentResponse(
                status='ask_user',
                message=message.content,
                tool_data=None
            )
