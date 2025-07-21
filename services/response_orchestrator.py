# services/response_orchestrator.py
from interfaces.orchestrators.response_orchestrator_interface import IResponseOrchestrator

class ResponseOrchestrator(IResponseOrchestrator):
    def __init__(self, ai_client, agents: dict):
        self.ai = ai_client
        self.agents = agents

    async def execute(self, context: list[dict], phone: str) -> list[dict]:
        system_prompt = {
            "role": "system",
            "content": (
                "Sua função é delegar a resposta da pergunta do usuário para o agente que melhor consegue responder. "
                "Você tem uma lista de cinco agentes: "
                "1. Agente_roteiro (#1), "
                "2. Agente_parques (#2), "
                "3. Agente_restaurante (#3), "
                "4. Agente_web (#4), "
                "5. Agente_filas (#5). "
                "Responda apenas com o código do agente. Caso esteja em dúvida, use o agente #1."
            ),
        }

        context = [system_prompt] + context

        response = await self.ai.chat(
            model="gpt-4o-mini",
            messages=context,
            temperature=0.5,
            max_tokens=488,
        )

        agent_code = response[0].get("content", "#1").strip()
        agent = self.agents.get(agent_code, self.agents["#1"])
        return await agent.execute(context=context, phone=phone)
