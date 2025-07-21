# agents/roteiro_agent.py

import json
from openai import OpenAI

# Importações necessárias da sua arquitetura
from interfaces.agents.agent_interface import IAgent
from container.clients import ClientContainer
from container.repositories import RepositoryContainer

class RoteiroAgent(IAgent):
    """
    Agente especialista em criar roteiros de viagem para Orlando.
    Ele conduz uma conversa para coletar dados e, ao final, aciona uma
    ferramenta para gerar o roteiro.
    """
    # --- Metadados do Agente ---
    id = "#1"
    name = "Agente de Roteiro de Viagem"
    description = "Agente especialista em criar roteiros de viagens para Orlando EUA."
    model = "gpt-4o-mini"
    _temperature = 0.5
    _max_tokens = 2048

    def __init__(self, client: OpenAI):
        """O construtor recebe o cliente da IA já inicializado."""
        self.client = client

    @property
    def instructions(self) -> str:
        """
        Propriedade que retorna as instruções de sistema (system prompt) para a IA.
        Extraído diretamente da sua especificação.
        """
        return """
Você é o "Orlando Trip Planner", uma IA especialista em criar roteiros personalizados para viagens a Orlando (Disney World, Universal, etc.), equilibrando parques, compras, gastronomia e descanso conforme o perfil do usuário.

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
        Extraído diretamente da sua especificação.
        """
        return [{
            "type": "function",
            "function": {
                "name": "roteiro",
                "description": "Gera um roteiro personalizado para viagem a Orlando com base em informações detalhadas dos viajantes.",
                "parameters": {
                    "type": "object",
                    "required": [
                        "data_chegada", "dias_completos_orlando", "numero_viajantes", "criancas", 
                        "ingressos_parques_comprados", "parques_desejados", "ritmo", "horario_preferido_acordar", 
                        "disposicao_fisica", "foco_viagem", "restricoes_alimentares", "reservas_restaurantes_tematicos", 
                        "interesse_gastronomico", "cafe_manha_personagens", "preferencia_refeicao", "meio_transporte", 
                        "hotel_ou_regiao", "usar_onibus_disney", "programacao_noturna", "passeios_externos", 
                        "lojas_prioritarias", "dias_compras_inteligente", "servicos_extras", "dia_livre", "motivo_viagem"
                    ],
                    "properties": {
                        "data_chegada": {"type": "string", "description": "Data de chegada em Orlando, no formato AAAA-MM-DD"},
                        "dias_completos_orlando": {"type": "integer", "description": "Quantidade de dias completos na cidade"},
                        "numero_viajantes": {"type": "integer", "description": "Número total de viajantes"},
                        "criancas": {"type": "array", "items": {"type": "integer"}, "description": "Lista de idades das crianças. Vazio se não houver."},
                        "ingressos_parques_comprados": {"type": "boolean", "description": "Se os ingressos já foram comprados"},
                        "parques_desejados": {"type": "array", "items": {"type": "string"}, "description": "Lista de parques que desejam visitar"},
                        "ritmo": {"type": "string", "enum": ["intenso", "equilibrado", "tranquilo"], "description": "Ritmo da viagem"},
                        "horario_preferido_acordar": {"type": "string", "description": "Horário preferido para acordar, ex: '08:00'"},
                        "disposicao_fisica": {"type": "string", "enum": ["baixa", "média", "alta"], "description": "Disposição física do grupo"},
                        "foco_viagem": {"type": "string", "description": "Foco da viagem (parques, compras, etc.)"},
                        "restricoes_alimentares": {"type": "string", "description": "Descrição de restrições alimentares"},
                        "reservas_restaurantes_tematicos": {"type": "boolean", "description": "Se já possuem reservas em restaurantes"},
                        "interesse_gastronomico": {"type": "boolean", "description": "Se tem interesse em experiências gastronômicas"},
                        "cafe_manha_personagens": {"type": "boolean", "description": "Se deseja café da manhã com personagens"},
                        "preferencia_refeicao": {"type": "string", "enum": ["fast-food", "refeições elaboradas", "ambas"]},
                        "meio_transporte": {"type": "string", "description": "Qual será o meio de transporte"},
                        "hotel_ou_regiao": {"type": "string", "description": "Nome do hotel ou região de hospedagem"},
                        "usar_onibus_disney": {"type": "boolean", "description": "Se pretendem usar o sistema de ônibus da Disney"},
                        "programacao_noturna": {"type": "boolean", "description": "Se precisam de sugestões para noite"},
                        "passeios_externos": {"type": "array", "items": {"type": "string"}, "description": "Interesse em passeios fora dos parques"},
                        "lojas_prioritarias": {"type": "array", "items": {"type": "string"}, "description": "Lojas que são prioridade"},
                        "dias_compras_inteligente": {"type": "string", "description": "Se gostariam de um 'roteiro de compras inteligente'"},
                        "servicos_extras": {"type": "array", "items": {"type": "string"}, "description": "Interesse em serviços extras"},
                        "dia_livre": {"type": "boolean", "description": "Se desejam ter algum dia completamente livre"},
                        "motivo_viagem": {"type": "string", "description": "Motivo da viagem (aniversário, primeira vez, etc.)"}
                    }
                }
            }
        }]

    @staticmethod
    def factory(client_container: "ClientContainer", repository_container: "RepositoryContainer") -> "IAgent":
        """Método fábrica que cria a instância do agente, injetando as dependências corretas."""
        openai_client = client_container.get("openai")
        return RoteiroAgent(client=openai_client)

    async def execute(self, customer: dict, orchestrator_output: list, context: list) -> str:
        """
        Ponto de entrada principal do agente. Gerencia o estado da conversa e chama a IA.
        """
        # Recupera o estado da conversa anterior ou inicializa um novo
        agent_context = next((item for item in context if item.get("agent_id") == self.id), None)
        state = agent_context['state'] if agent_context else {
            "conversation_history": [{"role": "system", "content": self.instructions}]
        }

        # Adiciona a última mensagem do usuário ao histórico
        last_user_message = orchestrator_output[-1]
        state['conversation_history'].append(last_user_message)
        
        # Chama a API da OpenAI com as instruções, ferramentas e histórico
        response = self.client.chat.completions.create(
            model=self.model,
            messages=state['conversation_history'],
            tools=self.tools,
            tool_choice="auto", # Deixa a IA decidir quando chamar a ferramenta
            temperature=self._temperature,
            max_tokens=self._max_tokens
        )
        
        message = response.choices[0].message
        
        # Prepara a resposta para o orquestrador
        output = {}

        # Cenário 1: A IA decidiu chamar a ferramenta 'roteiro'
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            arguments = json.loads(tool_call.function.arguments)
            output = {
                "response": {
                    "action": "tool_call", 
                    "tool_name": tool_call.function.name, 
                    "arguments": arguments
                },
                "context": {"agent_id": self.id, "state": state}
            }
        # Cenário 2: A IA precisa fazer mais perguntas ao usuário
        else:
            assistant_response = message.content
            # Adiciona a resposta da IA ao histórico para a próxima rodada
            state['conversation_history'].append({"role": "assistant", "content": assistant_response})
            output = {
                "response": {
                    "action": "ask_user", 
                    "message": assistant_response
                },
                "context": {"agent_id": self.id, "state": state}
            }
            
        return json.dumps(output, ensure_ascii=False)