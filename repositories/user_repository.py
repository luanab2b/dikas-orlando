from interfaces.repositories.user_repository_interface import IUserRepository

class UserRepository(IUserRepository):
    """
    Um repositório simulado para dados de usuários.
    Agora com capacidade de salvar novos usuários.
    """
    def __init__(self):
        self._users = {
            "12345": {"name": "Luana", "phone": "12345"},
            "67890": {"name": "Caroline", "phone": "67890"},
            "cli_test": {"name": "Amigo(a)", "phone": "cli_test"}
        }
        print("INFO: Repositório de usuários em memória inicializado.")

    def get_user_by_phone(self, phone: str) -> dict | None:
        return self._users.get(phone)

    def save_user(self, phone: str, name: str) -> dict:
        """Cria um novo usuário ou atualiza o nome de um existente."""
        if phone in self._users:
            self._users[phone]['name'] = name
        else:
            self._users[phone] = {"name": name, "phone": phone}
        
        print(f"INFO: Usuário salvo/atualizado: {self._users[phone]}")
        return self._users[phone]