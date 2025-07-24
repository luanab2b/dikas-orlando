from interfaces.agents.agent_interface import IAgent
from openai import OpenAI

class WebAgent(IAgent):
    id = "#4"
    name = "Agente_Web"
    model = "gpt-4o-mini" 
    description = (
        "Agente responsável por realizar pesquisas aprofundadas na web sobre Orlando, "
        "fornecendo informações completas, atualizadas e confiáveis sobre a cidade. O agente conhece desde atrações turísticas, "
        "parques, restaurantes, eventos, clima, hotéis, transporte, compras e curiosidades locais, até dicas práticas para moradores e visitantes. "
        "Sempre pronto para responder perguntas específicas ou apresentar sugestões personalizadas sobre qualquer assunto relacionado a Orlando."
    )
    instructions = (
        "Você é o especialista em Orlando. Sempre que receber uma solicitação, use suas habilidades de pesquisa na web para buscar e entregar informações detalhadas, "
        "relevantes e recentes sobre qualquer tema relacionado à cidade de Orlando. Ajude o usuário a planejar viagens, descobrir novidades, encontrar opções de lazer, "
        "gastronomia, hospedagem e solucionar dúvidas sobre a região. Se necessário, forneça links, recomendações e comparativos baseando-se em fontes confiáveis e atualizadas."
    )

    def __init__(self, client_container=None, repository_container=None):
        self.client_container = client_container
        self.repository_container = repository_container
        self.client = OpenAI()

    @staticmethod
    def factory(client_container, repository_container):
        return WebAgent(client_container, repository_container)

    def run(self, query: str, **kwargs) -> dict:
        """
        Recebe uma consulta do usuário e retorna uma resposta baseada em pesquisa web usando o modelo OpenAI.
        """
        response = self.client.responses.create(
            model=self.model,  # Sempre utilize o atributo da classe
            tools=[{"type": "web_search_preview"}],
            input=query,
        )
        # Extrai o texto da resposta
        output_text = ""
        if hasattr(response, "output") and response.output:
            for item in response.output:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            output_text += content.get("text", "")
        return {
            "text": output_text or "Não foi possível encontrar informações relevantes.",
            "raw_response": response
        }
        
    async def execute(self, context: list[dict], phone: str, user: dict) -> dict:
        """
        Executa o agente web, recebendo o contexto da conversa, telefone e dados do usuário.
        """
        last_user_message = [msg for msg in context if msg['role'] == 'user']
        if not last_user_message:
            return {"text": "Nenhuma mensagem de usuário encontrada no contexto."}
        query = last_user_message[-1]["content"]
        result = self.run(query)
        return result