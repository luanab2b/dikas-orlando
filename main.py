# main.py (com a anotação de tipo)
import asyncio
import json

from container.agents import AgentContainer
from container.clients import ClientContainer
from container.repositories import RepositoryContainer
from services.response_orchestrator import ResponseOrchestrator
# --- MUDANÇA 1: Importar a interface do repositório de conversas ---
from interfaces.repositories.conversation_repository_interface import IConversationRepository

async def main():
    print("Iniciando o sistema de agentes com o Orquestrador...")

    # --- 1. Preparação das Dependências ---
    client_container = ClientContainer()
    repository_container = RepositoryContainer()
    agent_container = AgentContainer(client_container, repository_container)
    
    all_agents_list = agent_container.all()
    print(f"Agentes registrados: {[agent.id for agent in all_agents_list]}")
    
    agents_dict = {agent.id: agent for agent in all_agents_list}
    
    ai_client = client_container.get("async_openai") 
    
    # --- 2. Raiz de Composição: Montando o Orquestrador ---
    orchestrator = ResponseOrchestrator(
        ai_client=ai_client, 
        agents=agents_dict, 
        repositories=repository_container
    )

    # --- 3. Lógica da Aplicação ---
    # --- MUDANÇA 2: Adicionamos a anotação de tipo aqui ---
    conversation_repo: IConversationRepository = repository_container.get("conversation")
    
    if not conversation_repo:
        raise RuntimeError("Erro crítico: Repositório de conversas não foi inicializado.")

    session_id = "cli_test_session" 
    history = conversation_repo.get_history(session_id)
    
    if not history:
        print("\n--- Início da Conversa com o Orquestrador ---")
    else:
        print(f"\n--- Continuando conversa da sessão {session_id} ---")
        
    print("Você pode perguntar sobre roteiros, parques, etc.")
    print("Digite 'sair' a qualquer momento para encerrar.")

    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() == 'sair':
            break

        history.append({"role": "user", "content": user_input})

        print("Orquestrador pensando...")
        agent_response_or_string = await orchestrator.execute(
            context=history, 
            phone="cli_test"
        )

        final_message = ""
        # Lógica de tratamento de resposta
        if isinstance(agent_response_or_string, list) and agent_response_or_string:
            final_message = agent_response_or_string[0].get("content", "Recebi uma resposta, mas sem conteúdo.")
        elif isinstance(agent_response_or_string, str):
            try:
                roteiro_output = json.loads(agent_response_or_string)
                response_data = roteiro_output.get('response', {})
                if response_data.get('action') == 'tool_call':
                    final_message = "Ok, tenho todas as informações! O roteiro seria gerado agora."
                else:
                    final_message = response_data.get('message', "Recebi uma resposta do agente, mas sem mensagem.")
            except json.JSONDecodeError:
                final_message = f"O agente retornou um texto inesperado: {agent_response_or_string}"
        else:
            final_message = f"Formato de resposta não reconhecido: {type(agent_response_or_string)}"

        print(f"\nAgente: {final_message}")
        history.append({"role": "assistant", "content": final_message})
        
        conversation_repo.save_history(session_id, history)

    print("\n--- Fim da Interação ---")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")