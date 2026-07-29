from fastapi import FastAPI, Request
from service import save_message, process_request , send_message
from llm import understand_message , translate_response
import base64
import os
import requests
from pydantic import BaseModel, Field
from reminder_service import send_reminder_to_all_groups
import scheduler 

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

class ReminderRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reminders.html"
    )

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    event = data.get("event")

    if event not in ["message", "message.any"]:
        return {"status": "ignored"}

    message = data.get("payload")

    if not message:
        return {"status": "no payload"}

    body = message.get("body")
    from_me = message.get("fromMe")

    print("\nNew message received:")
    # print("From:", message.get("from"))
    print("Body:", body)
    print("From me:", from_me)

    # print(json.dumps(data, indent=4, default=str))
    save_message(message)

    return {"status": "saved"}

@app.post("/test-farm")
async def test_farm(request: Request):
    try:
        data = await request.json()

        message_body = data.get("body")

        if not message_body:
            return {
                "status": "error",
                "message": "body is required"
            }

        print("Received:", message_body)

        parsed_data = understand_message(message_body)

        print("LLM Output:", parsed_data)

        result = process_request(parsed_data)

        print("Service result:", result)

        # Handle PDF response
        if isinstance(result, dict) and result.get("type") == "pdf":

            pdf_path = result["file"]

            print("PDF Path:", pdf_path)

            if not os.path.exists(pdf_path):
                raise FileNotFoundError(
                    f"PDF file not found: {pdf_path}"
                )

            with open(pdf_path, "rb") as pdf_file:
                pdf_base64 = base64.b64encode(
                    pdf_file.read()
                ).decode("utf-8")

            payload = {
                "session": "default",
                "chatId": "120363423099150354@g.us",
                "caption": "📄 Sunfra Farm Report",
                "file": {
                    "mimetype": "application/pdf",
                    "filename": os.path.basename(pdf_path),
                    "data": pdf_base64
                }
            }

            waha_response = requests.post(
                f"{BASE_URL}/api/sendFile",
                headers=HEADERS,
                json=payload,
                timeout=60
            )

            print("WAHA PDF status:", waha_response.status_code)
            print("WAHA PDF response:", waha_response.text)

            waha_response.raise_for_status()  
        else:
            language = parsed_data.get("language", "en")

            reply = translate_response(
                result,
                language
            )

            send_message(
                chat_id="120363423099150354@g.us",
                text=reply
            )

        return {
            "status": "processed",
            "parsed_data": parsed_data,
            "result": result
        }

    except Exception as e:
        print(e)
        return {
            "status": "error",
            "message": str(e)
        }

@app.post("/test-customer")
async def test_customer(request: Request):

    body = await request.json()

    message = body.get("message")

    llm_output = understand_message(message)

    result = process_request(
        llm_output,
        chat_id="919876543210@c.us",
        customer_whatsapp="919876543210"
    )

    return result

@app.post("/send-group-reminder")
def send_group_reminder(request: ReminderRequest):

    result = send_reminder_to_all_groups(request.message)

    return {
        "success": True,
        "results": result
    }

