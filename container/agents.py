# container/agents.py
import pkgutil
import importlib
import inspect
from interfaces.agents.agent_interface import IAgent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from container.clients import ClientContainer
    from container.repositories import RepositoryContainer

class AgentContainer:
    """Responsável por descobrir, registrar e fornecer acesso a todos os agentes."""
    def __init__(self, clients: "ClientContainer", repositories: "RepositoryContainer"):
        self._clients = clients
        self._repositories = repositories
        self._agents: dict[str, IAgent] = {}
        self._register_agents()

    def _register_agents(self):
        import agents
        print("INFO: Iniciando o registro dinâmico de agentes...")
        for _, module_name, _ in pkgutil.iter_modules(agents.__path__, f"{agents.__name__}."):
            try:
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, IAgent) and obj is not IAgent and not inspect.isabstract(obj):
                        agent_instance = obj.factory(self._clients, self._repositories)
                        if agent_instance.id in self._agents:
                            raise ValueError(f"ID de agente duplicado: {agent_instance.id}")
                        self._agents[agent_instance.id] = agent_instance
                        print(f"SUCCESS: Agente '{agent_instance.name}' (ID: {agent_instance.id}) registrado.")
            except Exception as e:
                print(f"WARNING: Falha ao carregar agente do módulo '{module_name}'. Erro: {e}")

    def get(self, agent_id: str) -> IAgent | None:
        return self._agents.get(agent_id)

    def all(self) -> list[IAgent]:
        return list(self._agents.values())
