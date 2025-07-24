# container/repositories.py

from repositories.message_repository import MessageRepository
from repositories.conversation_repository import InMemoryConversationRepository, FileSystemConversationRepository
from repositories.user_repository import UserRepository

class RepositoryContainer:
    def __init__(self):
        self._repositories = {}
        
        # Inicializa o repositório de mensagens
        self._repositories["message"] = None  # Será inicializado quando um cliente DB for fornecido
        
        # Inicializa o repositório de conversas (em memória por padrão)
        self._repositories["conversation"] = InMemoryConversationRepository()
        
        # Inicializa o repositório de usuários
        self._repositories["user"] = UserRepository()
        print("INFO: Repositório de usuários em memória inicializado.")
        
    def initialize_db_repositories(self, db_client):
        """
        Inicializa repositórios que dependem do cliente de banco de dados.
        """
        # Inicializa o repositório de mensagens com o cliente de banco de dados
        self._repositories["message"] = MessageRepository(db_client)
        print("INFO: Repositório de mensagens inicializado com o cliente de banco de dados.")
        
        # Opcionalmente, você pode substituir o repositório de conversas em memória por um baseado em banco de dados
        # from repositories.conversation_repository import DatabaseConversationRepository
        # self._repositories["conversation"] = DatabaseConversationRepository(db_client)
        
    def get(self, name):
        """
        Obtém um repositório pelo nome.
        """
        return self._repositories.get(name)