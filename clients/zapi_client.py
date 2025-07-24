import os
from dotenv import load_dotenv
load_dotenv()

class ZAPIClient:
    def __init__(self):
        # Carrega os parâmetros de conexão das variáveis de ambiente
        self.base_url = os.getenv("ZAPI_BASE_URL")
        self.instance_id = os.getenv("ZAPI_INSTANCE_ID")
        self.instance_token = os.getenv("ZAPI_INSTANCE_TOKEN")
        self.client_token = os.getenv("ZAPI_CLIENT_TOKEN")
        self.headers = {"Content-Type": "application/json"}
        
        print(f"🔧 ZAPI configurada com: \nURL: {self.base_url}\nID: {self.instance_id}")

    def get_connection_info(self):
        return {
            "base_url": self.base_url,
            "instance_id": self.instance_id,
            "instance_token": self.instance_token,
            "client_token": self.client_token,
            "headers": self.headers,
        }

# Instância global, pronta para importar em outros módulos
zapi_client = ZAPIClient()