# agents/roteiro_agent.py
import json
import os
import sys
from openai import AsyncOpenAI
from utils.pdf_utils import gerar_pdf_base64
from services.send_pdf_service import send_pdf_via_whatsapp
from openai.types.chat import ChatCompletionMessageParam
from interfaces.agents.agent_interface import IAgent, AgentResponse
from typing import TYPE_CHECKING
from services.itinerary_generator_service import ItineraryGeneratorService

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
    NAME = "Agente_Roteiro"
    MODEL = "gpt-4o-mini"
    TEMPERATURE = 0.5
    MAX_TOKENS = 2048

    def __init__(self, client: AsyncOpenAI):
        """O construtor recebe o cliente da IA já inicializado."""
        self.client = client
        self.itinerary_service = ItineraryGeneratorService(client)
        self.collected_data = {}

    # --- Implementação das Propriedades da Interface ---
    @property
    def id(self) -> str:
        return self.ID

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def system(self) -> str:
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
                - Nunca gere o roteiro diretamente, apenas acione a function 'roteiro' com os dados coletados.
            """

    @property
    def tools(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": "roteiro",
                    "description": "Gera um roteiro personalizado para viagem a Orlando com base em informações detalhadas dos viajantes.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "data_chegada": {
                                "type": "string",
                                "description": "Data de chegada em Orlando, no formato AAAA-MM-DD"
                            },
                            "data_retorno": {
                                "type": "string",
                                "description": "Data de retorno, no formato AAAA-MM-DD"
                            },
                            "dias_completos_orlando": {
                                "type": "integer",
                                "description": "Quantidade de dias completos na cidade"
                            },
                            "numero_viajantes": {
                                "type": "integer",
                                "description": "Número total de viajantes"
                            },
                            "criancas": {
                                "type": "array",
                                "description": "Lista de idades das crianças viajantes. Se não houver crianças, deixar vazio.",
                                "items": {
                                    "type": "integer",
                                    "description": "Idade da criança"
                                }
                            },
                            "ingressos_parques_comprados": {
                                "type": "boolean",
                                "description": "Se os ingressos dos parques já estão comprados"
                            },
                            "parques_desejados": {
                                "type": "array",
                                "description": "Lista de parques definidos que deseja visitar",
                                "items": {
                                    "type": "string",
                                    "description": "Nome do parque desejado"
                                }
                            },
                            "ritmo": {
                                "type": "string",
                                "description": "Ritmo da viagem: intenso, equilibrado ou tranquilo",
                                "enum": [
                                    "intenso",
                                    "equilibrado",
                                    "tranquilo"
                                ]
                            },
                            "horario_preferido_acordar": {
                                "type": "string",
                                "description": "Horário preferido para acordar, exemplo: '07:00'"
                            },
                            "disposicao_fisica": {
                                "type": "string",
                                "description": "Nível de disposição física para caminhadas/filas: baixa, média ou alta",
                                "enum": [
                                    "baixa",
                                    "média",
                                    "alta"
                                ]
                            },
                            "foco_viagem": {
                                "type": "string",
                                "description": "Foco principal da viagem: parques, compras, restaurantes, passeios externos ou mistura",
                                "enum": [
                                    "parques",
                                    "compras",
                                    "restaurantes",
                                    "passeios externos",
                                    "mistura"
                                ]
                            },
                            "restricoes_alimentares": {
                                "type": "string",
                                "description": "Restrições alimentares de algum viajante"
                            },
                            "reservas_restaurantes_tematicos": {
                                "type": "boolean",
                                "description": "Se há reservas já feitas em restaurantes temáticos"
                            },
                            "interesse_gastronomico": {
                                "type": "boolean",
                                "description": "Interesse em experiências gastronômicas diferentes"
                            },
                            "cafe_manha_personagens": {
                                "type": "boolean",
                                "description": "Deseja café da manhã com personagens"
                            },
                            "preferencia_refeicao": {
                                "type": "string",
                                "description": "Prefere fast-food, refeições elaboradas ou ambas",
                                "enum": [
                                    "fast-food",
                                    "refeições elaboradas",
                                    "ambas"
                                ]
                            },
                            "meio_transporte": {
                                "type": "string",
                                "description": "Meio de transporte principal: carro, Uber, shuttle, etc."
                            },
                            "hotel_ou_regiao": {
                                "type": "string",
                                "description": "Nome do hotel ou região de hospedagem"
                            },
                            "usar_onibus_disney": {
                                "type": "boolean",
                                "description": "Se vai utilizar os ônibus Disney"
                            },
                            "programacao_noturna": {
                                "type": "boolean",
                                "description": "Se precisa de programação noturna no roteiro"
                            },
                            "passeios_externos": {
                                "type": "array",
                                "description": "Lista de passeios fora dos parques como outlets, Disney Springs, ICON Park, etc.",
                                "items": {
                                    "type": "string",
                                    "description": "Nome do passeio externo"
                                }
                            },
                            "lojas_prioritarias": {
                                "type": "array",
                                "description": "Lojas prioritárias para visita",
                                "items": {
                                    "type": "string",
                                    "description": "Nome da loja prioritária"
                                }
                            },
                            "dias_compras_inteligente": {
                                "type": "integer",
                                "description": "Número de dias dedicados ao roteiro de compras inteligente"
                            },
                            "servicos_extras": {
                                "type": "array",
                                "description": "Serviços extras desejados (chip, carrinho, Memory Maker…)",
                                "items": {
                                    "type": "string",
                                    "description": "Nome do serviço extra"
                                }
                            },
                            "dia_livre": {
                                "type": "boolean",
                                "description": "Se deseja reservar um dia livre"
                            },
                            "motivo_viagem": {
                                "type": "string",
                                "description": "Motivo principal da viagem (ex: aniversário, presente, primeira vez, etc.)"
                            }
                        },
                        "required": [
                            "data_chegada",
                            "data_retorno",
                            "dias_completos_orlando",
                            "numero_viajantes",
                            "criancas",
                            "ingressos_parques_comprados",
                            "parques_desejados",
                            "ritmo",
                            "horario_preferido_acordar",
                            "disposicao_fisica",
                            "foco_viagem",
                            "restricoes_alimentares",
                            "reservas_restaurantes_tematicos",
                            "interesse_gastronomico",
                            "cafe_manha_personagens",
                            "preferencia_refeicao",
                            "meio_transporte",
                            "hotel_ou_regiao",
                            "usar_onibus_disney",
                            "programacao_noturna",
                            "passeios_externos",
                            "lojas_prioritarias",
                            "dias_compras_inteligente",
                            "servicos_extras",
                            "dia_livre",
                            "motivo_viagem"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        ]
                

    @staticmethod
    def factory(client_container: "ClientContainer", repository_container: "RepositoryContainer") -> "IAgent":
        """Método fábrica que cria a instância do agente, injetando as dependências corretas."""
        openai_client = client_container.get("async_openai")
        if not openai_client:
            raise ValueError("Cliente 'async_openai' não encontrado.")
        return RoteiroAgent(client=openai_client)

    async def execute(self, context: list[dict], phone: str, user: dict | None) -> dict:
        """
        Ponto de entrada principal do agente. A assinatura agora é compatível.
        """
        user_name = user['name'] if user and user.get('name') else "Viajante"
        
        # O 'context' recebido já é o histórico completo da conversa
        messages: list[ChatCompletionMessageParam] = [{"role": "system", "content": self.system}]

        if len(context) == 0:
            # Se for a primeira mensagem, adiciona uma saudação personalizada
            messages.extend([
                {"role": "user", "content": "Olá, quero um roteiro para Orlando."},
                {"role": "assistant", "content": f"Olá, {user_name}! Com certeza! Para criar o roteiro perfeito para sua viagem a Orlando, preciso de algumas informações importantes. Vamos começar:"}
            ])
        
        # Adicionando o histórico da conversa
        messages.extend(context)
        
        response = await self.client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            tools=self.tools,
            tool_choice="auto",
            temperature=self.TEMPERATURE,
            max_tokens=self.MAX_TOKENS
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            if function_name == "roteiro":
                print("INFO: Todas as informações coletadas! Gerando roteiro...")
                roteiro = await self.roteiro(arguments, phone)
                return {
                    'status': 'final_answer',
                    'message': roteiro
                }
        
        # Se não houver tool_calls, retorna a mensagem da IA (que deve ser uma pergunta)
        return {
            'status': 'collecting_data',
            'message': message.content or "Por favor, forneça mais informações para seu roteiro."
        }
            
    async def roteiro(self, dados_coletados: dict, phone: str) -> str:
        """
        Função que envia os dados coletados para o serviço de geração de roteiro.
        Esta função é chamada quando todas as informações obrigatórias forem coletadas.

        Args:
            dados_coletados (dict): Dicionário com todos os dados coletados do usuário.
            phone (str): Número de telefone para enviar o PDF.
            
        Returns:
            str: O roteiro personalizado gerado
        """
        print("INFO: Gerando roteiro com os dados coletados...")
        roteiro_final = await self.itinerary_service.generate(dados_coletados)
        
        print("INFO: Convertendo roteiro para PDF...")
        pdf_base64 = gerar_pdf_base64(roteiro_final)
        
        print(f"INFO: Enviando PDF para {phone}...")
        enviado = send_pdf_via_whatsapp(phone, pdf_base64)
        
        if enviado:
            return "Seu roteiro personalizado para Orlando está pronto! Acabei de enviar o PDF pelo WhatsApp. 😊 Qualquer dúvida sobre o roteiro, é só me perguntar!"
        else:
            return "Seu roteiro está pronto, mas encontrei um problema ao enviar o PDF pelo WhatsApp. Por favor, tente novamente ou entre em contato com o suporte."