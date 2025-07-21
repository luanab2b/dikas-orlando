# container/agent_container.py

import pkgutil
import importlib
import agents 
from interfaces.agents.agent_interface import IAgent
from container.clients import ClientContainer
from container.repositories import RepositoryContainer

class AgentContainer:
    """
    Responsável por descobrir, registrar e fornecer acesso a todos os agentes
    disponíveis no sistema de forma dinâmica.
    """

    def __init__(self, clients: ClientContainer, repositories: RepositoryContainer):
        self._clients = clients
        self._repositories = repositories
        self._agents: list[IAgent] = []
        self._register_agents()

    def _register_agents(self):
        """
        Varre o pacote 'agents', importa os módulos e registra as classes de agente válidas.
        """
        print("INFO: Iniciando o registro dinâmico de agentes...")
        agents_id: list[str] = []

        # Itera sobre todos os módulos dentro do pacote 'agents'
        for _, module_name, _ in pkgutil.iter_modules(agents.__path__, f"{agents.__name__}."):
            try:
                # Importa o módulo dinamicamente
                module = importlib.import_module(module_name)
                print(f"INFO: Verificando módulo '{module_name}'...")

                # Procura por classes dentro do módulo que implementam IAgent
                for attr in dir(module):
                    obj = getattr(module, attr)
                    if (
                        isinstance(obj, type)
                        and issubclass(obj, IAgent)
                        and obj is not IAgent  # Garante que não é a própria interface
                        and hasattr(obj, "factory")
                    ):
                        print(f"INFO: Agente '{obj.__name__}' encontrado. Instanciando via factory...")
                        # Usa a factory para criar uma instância do agente
                        agent = obj.factory(
                            client_container=self._clients,
                            repository_container=self._repositories,
                        )

                        if agent:
                            if agent.id in agents_id:
                                raise ValueError(f"Erro Crítico: ID de agente duplicado encontrado: {agent.id}")

                            agents_id.append(agent.id)
                            self._agents.append(agent)
                            print(f"SUCCESS: Agente '{agent.name}' (ID: {agent.id}) registrado com sucesso.")

            except Exception as e:
                print(f"WARNING: Falha ao carregar o módulo de agente '{module_name}'. Erro: {e}")

    def get(self, agent_id: str) -> IAgent | None:
        """
        Retorna uma instância de um agente específico pelo seu ID.
        """
        return next((agent for agent in self._agents if agent.id == agent_id), None)

    def all(self) -> list[IAgent]:
        """
        Retorna a lista de todas as instâncias de agentes registrados.
        """
        return self._agents