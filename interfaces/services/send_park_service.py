import os
import requests
from dotenv import load_dotenv
from utils.orlando_parks import get_orlando_parks

# Carrega as variáveis do arquivo .env
load_dotenv()

def send_message(phone_number, message):
    """
    Envia uma mensagem genérica via Evolution API
    
    Args:
        phone_number (str): Número do WhatsApp (formato: 5511999999999)
        message (str): Conteúdo da mensagem
    
    Returns:
        tuple: (status_code, response)
    """
    # Obter credenciais da Evolution API
    instance_id = os.getenv("EVOLUTION_INSTANCE_ID")
    token = os.getenv("EVOLUTION_TOKEN")
    
    if not instance_id or not token:
        return None, "Credenciais da Evolution API não configuradas"
    
    # Enviar via Evolution API
    url = f"https://api.evolution-api.com.br/instances/{instance_id}/token/{token}/send-message"
    
    payload = {
        "to": phone_number,
        "type": "text",
        "message": message
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.status_code, "Mensagem enviada com sucesso!"
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem: {e}")
        return None, str(e)

def send_parks_list(phone_number):
    """
    Envia a lista de parques de Orlando via Evolution API
    
    Args:
        phone_number (str): Número do WhatsApp (formato: 5511999999999)
    
    Returns:
        tuple: (status_code, response)
    """
    # Obter lista de parques usando sua função existente
    _, lista_numerada = get_orlando_parks()
    
    # Montar mensagem
    mensagem = f"🎢 *Parques disponíveis em Orlando* 🎢\n\n{lista_numerada}"
    
    # Reutilizar a função de envio
    return send_message(phone_number, mensagem)