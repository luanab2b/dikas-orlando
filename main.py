# main.py
import asyncio
import json
from container.agents import AgentContainer
from container.clients import ClientContainer
from container.repositories import RepositoryContainer

async def main():
    print("Iniciando o sistema de agentes...")

    # 1. Inicializa os containers de dependência
    client_container = ClientContainer()
    repository_container = RepositoryContainer()

    # 2. Inicializa o container de agentes, que vai descobrir e registrar o RoteiroAgent
    agent_container = AgentContainer(client_container, repository_container)

    # 3. Recupera o Agente_roteiro pelo seu ID
    roteiro_agent = agent_container.get("#1")

    if not roteiro_agent:
        print("Erro: Agente de roteiro não encontrado. Verifique o ID ou o processo de registro.")
        return

    print(f"Agente encontrado: {roteiro_agent.name} (ID: {roteiro_agent.id})")

    orchestrator_output = []
    # O contexto do agente é armazenado aqui para manter o estado da conversa
    agent_context_state = {}

    print("\n--- Início da Conversa com o Agente_roteiro ---")
    print("Digite 'sair' a qualquer momento para encerrar.")

    # Primeira interação simulada para iniciar a conversa
    user_input = "Olá, quero planejar uma viagem para Orlando."

    while True:
        print(f"\nVocê: {user_input}")
        orchestrator_output.append({"role": "user", "content": user_input})

        # Prepara o contexto para o agente.
        # Ele espera uma lista de dicionários, onde cada um pode ter um 'agent_id' e seu 'state'.
        current_context_for_agent = [{"agent_id": roteiro_agent.id, "state": agent_context_state}] if agent_context_state else []

        # Executa o agente com a entrada do usuário e o contexto atual
        agent_response_json = await roteiro_agent.execute(
            customer={}, # Informações do cliente, se houver
            orchestrator_output=orchestrator_output,
            context=current_context_for_agent
        )

        agent_output = json.loads(agent_response_json)
        response_content = agent_output['response']
        new_agent_state = agent_output['context']['state']
        agent_context_state = new_agent_state.get("collected_data", {}) # Atualiza o estado para a próxima iteração

        if response_content['action'] == "tool_call":
            print("\n--- Agente acionou a função 'roteiro'! ---")
            print(f"Nome da Ferramenta: {response_content['tool_name']}")
            print(f"Argumentos Coletados:")
            print(json.dumps(response_content['arguments'], indent=2, ensure_ascii=False))
            print("\nO roteiro seria gerado agora com base nestes dados.")
            break # Encerra o loop, pois o agente coletou tudo

        elif response_content['action'] == "ask_user":
            print(f"\nAgente: {response_content['message']}")
            user_input = input("Sua resposta: ")
            if user_input.lower() == 'sair':
                print("Conversa encerrada.")
                break
            # O loop continua com a nova entrada do usuário
        else:
            print(f"Agente: Resposta desconhecida: {response_content}")
            break

    print("\n--- Fim da Interação ---")

if __name__ == "__main__":
    asyncio.run(main())