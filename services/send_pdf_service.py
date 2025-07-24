import requests
import os

def send_pdf_via_whatsapp(phone, pdf_base64):
    # Carrega as variáveis de ambiente (ajuste conforme seu projeto)
    base_url = os.getenv("ZAPI_BASE_URL")
    instance_id = os.getenv("ZAPI_INSTANCE_ID")
    instance_token = os.getenv("ZAPI_INSTANCE_TOKEN")
    client_token = os.getenv("ZAPI_CLIENT_TOKEN")

    url = f"{base_url}/instances/{instance_id}/token/{instance_token}/send-file-base64"
    payload = {
        "phone": phone,
        "filename": "roteiro.pdf",
        "base64": pdf_base64,
        "caption": "Seu roteiro personalizado!"
    }
    headers = {
        "Content-Type": "application/json",
        "Client-Token": client_token
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.status_code == 200