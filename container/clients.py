# container/clients.py
from openai import OpenAI

class ClientContainer:
    def __init__(self):
        self._clients = {
            "openai": OpenAI() # Inicializa o cliente OpenAI
        }

    def get(self, client_name: str):
        return self._clients.get(client_name)