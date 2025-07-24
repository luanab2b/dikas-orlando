import asyncio
import json

from container.agents import AgentContainer
from container.clients import ClientContainer
from container.repositories import RepositoryContainer
from services.response_orchestrator import ResponseOrchestrator
from interfaces.repositories.conversation_repository_interface import IConversationRepository

async def main():
    print("Iniciando o sistema de agentes com o Orquestrador...")

    client_container = ClientContainer()
    repository_container = RepositoryContainer()
    agent_container = AgentContainer(client_container, repository_container)
    
    all_agents_list = agent_container.all()
    
    # Filtrar apenas os objetos válidos (não strings)
    valid_agents = [agent for agent in all_agents_list if not isinstance(agent, str)]
    
    # Exibir informações sobre agentes
    if valid_agents:
        print(f"Agentes registrados: {[agent.id for agent in valid_agents]}")
    else:
        print("Aviso: Nenhum agente válido foi registrado.")
    
    agents_dict = {agent.id: agent for agent in valid_agents}
    
    ai_client = client_container.get("async_openai") 
    
    orchestrator = ResponseOrchestrator(
        ai_client=ai_client, 
        agents=agents_dict, 
        repositories=repository_container
    )

    # Importar aqui para evitar erros de importação circular
    from interfaces.repositories.conversation_repository_interface import IConversationRepository
    
    conversation_repo: IConversationRepository = repository_container.get("conversation")
    
    if not conversation_repo:
        raise RuntimeError("Erro crítico: Repositório de conversas não foi inicializado.")

    print("\n--- Fim da Interação ---")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")