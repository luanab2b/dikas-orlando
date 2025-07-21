# interfaces/repositories/user_repository_interface.py
from abc import ABC, abstractmethod

class IUserRepository(ABC):
    """
    Define o contrato para o repositório de usuários.
    """
    @abstractmethod
    def get_user_by_phone(self, phone: str) -> dict | None:
        """Busca um usuário pelo número de telefone."""
        pass

    @abstractmethod
    def save_user(self, phone: str, name: str) -> dict:
        """Cria ou atualiza um usuário."""
        pass