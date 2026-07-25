from fastapi import FastAPI, Request
from service import save_message
import json

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Webhook server is running"}


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    event = data.get("event")

    if event not in ["message", "message.any"]:
        return {"status": "ignored"}

    message = data.get("payload")

    if not message:
        return {"status": "no payload"}

    print("\nNew message received:")
    # print("From:", message.get("from"))
    print("Body:", message.get("body"))
    print("From me:", message.get("fromMe"))

    # print(json.dumps(data, indent=4, default=str))
    save_message(message)

    return {"status": "saved"}