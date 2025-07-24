import asyncio
from agents.roteiro_agent import RoteiroAgent
from agents.web_agent import WebAgent
from container.clients import ClientContainer
from container.repositories import RepositoryContainer
from services.response_orchestrator import ResponseOrchestrator

async def main():
    client_container = ClientContainer()
    repository_container = RepositoryContainer()
    ai_client = client_container.get("async_openai")

    roteiro_agent = RoteiroAgent(ai_client)
    web_agent = WebAgent(client_container, repository_container)

    agents = {
        "#1": roteiro_agent,
        "#4": web_agent,
    }

    orchestrator = ResponseOrchestrator(
        ai_client=ai_client,
        agents=agents,
        repositories=repository_container
    )
    print("Sistema iniciado com sucesso.")

if __name__ == "__main__":
    asyncio.run(main())