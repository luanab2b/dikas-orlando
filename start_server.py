from fastapi import FastAPI, Request
from interfaces.orchestrators.whatsapp_orchestrator import process_message

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data["message"]["body"]
    sender = data["message"]["from"]
    process_message(message, sender)
    return {"status": "ok"}