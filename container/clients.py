# container/clients.py

from openai import OpenAI, AsyncOpenAI 
from dotenv import load_dotenv
import os

class ClientContainer:
    def __init__(self):
        load_dotenv() 

        self.clients = {
            "openai": OpenAI(), 
            "async_openai": AsyncOpenAI() 
        }

    def get(self, client_name: str):
        client = self.clients.get(client_name)
        if not client:
            raise ValueError(f"Cliente '{client_name}' não registrado.")
        return client