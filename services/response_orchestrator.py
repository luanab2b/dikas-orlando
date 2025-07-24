from interfaces.orchestrators.response_orchestrator_interface import IResponseOrchestrator
from container.repositories import RepositoryContainer
from typing import Coroutine, Any

class ResponseOrchestrator(IResponseOrchestrator):
    """
    Orquestrador responsável por:
    1. Usar instruções detalhadas para delegar a um agente.
    2. Buscar dados do usuário para passar ao agente.
    """
    # O construtor recebe o container de repositórios
    def __init__(self, ai_client, agents: dict, repositories: RepositoryContainer):
        self.ai = ai_client
        self.agents = agents
        user_repo = repositories.get("user")
        if not user_repo:
            raise ValueError("Repositório de usuário ('user') não encontrado no container.")
        self.user_repo = user_repo

    async def execute(self, context: list[dict], phone: str) -> Coroutine[Any, Any, list[dict] | str]:
        instructions = (
            "Sua função é delegar a resposta da pergunta do usuário para o agente que melhor consegue responder. "
            "Você tem uma lista de cinco agente aos quais você pode delegar essas resposta: "
            "1. Agente_roteiro: Esse agente é especialista em criar roteiros de viagens para Orlando EUA. Sempre que for acionar esse agente(Agente_roteiro), responda apenas o código '#1'. "
            "2. Agente_parques: Esse agente é especialista em parques de Orlando, e sabe tudo sobre eles. Sempre que for acionar esse agente (Agente_parques), responda apenas o código '#2'. "
            "3. Agente_restaurante: Esse agente é especialista em restaurantes de Orlando. Sempre que for acionar esse agente (Agente_restaurante), responda apenas o código '#3'. "
            "4. Agente_web: Esse agente é especialista em buscar na web informações que os outros agentes não conseguem dar sobre Orlando. Sempre que for acionar esse agente (Agente_web), responda apenas o código '#4'. "
            "5. Agente_filas: Esse agente é especialista em verificar como estão as filas em parques de Orlando. Sempre que for acionar esse agente (Agente_filas), responda apenas o código '#5'.  "
            "Responda apenas com o código do agente selecionado. Nunca responda outra coisa a não ser o código do agente escolhido. "
            "Caso não tenha bem definido para quem passar a resposta, encaminhar para o Agente_roteiro. Sempre que for acionar esse agente(Agente_roteiro), responda apenas o código '#1'."
        )

        # O contexto para a IA do orquestrador usa as instruções e a última mensagem do usuário
        last_user_message = [msg for msg in context if msg['role'] == 'user'][-1:]
        messages_for_api = [
            {"role": "system", "content": instructions}
        ] + last_user_message

        # Chamada à API de IA
        response = await self.ai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages_for_api,
            temperature=0.5,
            max_tokens=488
        )

        agent_code = response.choices[0].message.content.strip()

        # Mantém a lógica de fallback
        if agent_code not in self.agents:
            agent_code = "#1"

        agent = self.agents.get(agent_code)
        if not agent:
            raise ValueError(f"Agente com código '{agent_code}' não foi encontrado.")

        # Busca o usuário e o passa para o agente 
        user = self.user_repo.get_user_by_phone(phone)

        # O contexto COMPLETO é passado para o agente final, junto com os dados do usuário
        return await agent.execute(context=context, phone=phone, user=user)