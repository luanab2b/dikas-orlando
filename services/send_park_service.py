import os
import requests
import re
import time
import random
from dotenv import load_dotenv
from utils.orlando_parks import get_orlando_parks

# Carrega as variáveis do arquivo .env
load_dotenv()

class ZAPIService:
    def __init__(self):
        # Usando as variáveis de ambiente configuradas
        self._base_url = os.getenv("ZAPI_BASE_URL")
        self._instance_id = os.getenv("ZAPI_INSTANCE_ID")
        self._instance_token = os.getenv("ZAPI_INSTANCE_TOKEN")
        self._client_token = os.getenv("ZAPI_CLIENT_TOKEN")
        self._headers = {"Content-Type": "application/json"}
        
        print(f"🔧 ZAPI configurada com: \nURL: {self._base_url}\nID: {self._instance_id}")
        
    def __validate_message(self, message: str) -> bool:
        # Trata a mensagem
        message_clean = message.strip()

        # Verifica se a mensagem não está vazia
        if not message_clean:
            print("❌ Dados incompletos: A mensagem é obrigatória.")
            return False

        return True

    def __validate_cell_number(self, cell_number: str) -> bool:
        # Verifica se o celular não está vazio
        if not cell_number:
            print(f"[Z-API] ❌ Dados incompletos: O número de telefone é obrigatório.")
            return False

        # Trata o telefone
        cell_number_clean = cell_number.strip()

        # Remove caracteres não numéricos
        cell_number_clean = re.sub(r"[^0-9]", "", cell_number_clean)

        # Verifica tamanho mínimo (11 dígitos = DDD + Celular)
        if len(cell_number_clean) < 11:
            print(f"[Z-API] Telefone inválido. O número de celular deve conter no mínimo 11 dígitos (com DDD): {cell_number_clean}")
            return False

        # Verifica tamanho máximo (13 dígitos = 55 + DDD + Celular)
        if len(cell_number_clean) > 13:
            print(f"[Z-API] Telefone inválido. O número de celular deve conter no máximo 13 dígitos (com DDI e DDD): {cell_number_clean}")
            return False

        return True

    def _resolve_phone(self, phone: str) -> str:
        # Remove caracteres não numéricos
        phone_clean = re.sub(r"[^0-9]", "", phone)
        
        # Adiciona o DDI 55 caso não tenha
        if not phone_clean.startswith("55") and len(phone_clean) <= 11:
            return f"55{phone_clean}"

        return phone_clean

    def _resolve_url(self) -> str:
        return f"{self._base_url}/instances/{self._instance_id}/token/{self._instance_token}"

    def send_message(self, phone: str, message: str) -> tuple:
        if not self.__validate_message(message) or not self.__validate_cell_number(phone):
            print(f"[Z-API] Dados incompletos: mensagem: {message}, telefone: {phone}")
            return None, "Dados inválidos"

        url = self._resolve_url() + "/send-text"
        headers = {**self._headers, "Client-Token": self._client_token}
        resolved_phone = self._resolve_phone(phone)
        
        payload = {
            "phone": resolved_phone,
            "message": message
        }

        try:
            print(f"[Z-API] Enviando mensagem para {resolved_phone}")
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            print(f"[Z-API] Resposta: {response.status_code}")
            
            return 200, "Mensagem enviada com sucesso!"
        except Exception as e:
            print(f"[Z-API] ❌ Falha ao enviar mensagem: {str(e)}")
            return None, str(e)

# Criando a instância global do serviço
zapi_service = ZAPIService()

def send_message(phone_number, message):
    """
    Envia uma mensagem genérica via ZAPI
    
    Args:
        phone_number (str): Número do WhatsApp (formato: 5511999999999)
        message (str): Conteúdo da mensagem
    
    Returns:
        tuple: (status_code, response)
    """
    return zapi_service.send_message(phone_number, message)

def send_parks_list(phone_number):
    """
    Envia a lista de parques de Orlando via ZAPI
    
    Args:
        phone_number (str): Número do WhatsApp (formato: 5511999999999)
    
    Returns:
        tuple: (status_code, response)
    """
    # Obter lista de parques através do módulo utilitário
    parks, lista_numerada = get_orlando_parks()
    
    if not parks:
        return None, "Não foi possível obter a lista de parques"
    
    # Montar mensagem
    mensagem = (
        f"🎢 *Parques disponíveis em Orlando* 🎢\n\n"
        f"{lista_numerada}\n\n"
        f"Para consultar as filas, responda apenas com o número do parque desejado."
    )
    
    # Reutilizar a função de envio
    return send_message(phone_number, message=mensagem)