from fastapi import FastAPI, Request
from service import save_message, process_request , send_message , create_reminder , edit_report, remove_report
from llm import understand_message , translate_response
import base64
import os
import requests
from pydantic import BaseModel, Field
import scheduler 
from typing import List, Optional

from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from service import fetch_all_reminders , remove_reminder , change_reminder_status , create_saved_contact, fetch_saved_contacts, remove_saved_contact , create_reminder , create_report , fetch_reports 
from contextlib import asynccontextmanager
from scheduler import start_scheduler, stop_scheduler\

from datetime import date
from reminder_service import get_whatsapp_recipients

@asynccontextmanager
async def lifespan(app: FastAPI):

    start_scheduler()

    yield

    stop_scheduler()



app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)
from typing import List, Optional
from pydantic import BaseModel


class ReminderRecipientRequest(BaseModel):
    recipient_name: str
    chat_id: str
    recipient_type: str

class ReminderCreateRequest(BaseModel):
    report_id: int
    message: str
    repeat_type: str

    schedule_date: Optional[str] = None

    schedule_time: str

    week_day: Optional[str] = None

    recipients: List[ReminderRecipientRequest]

class ReminderStatusRequest(BaseModel):
    is_active: bool

class SavedContactRequest(BaseModel):
    name: str
    whatsapp_number: str

class ReminderReportRequest(BaseModel):
    report_name: str
    task_title: str
    message: str
    details: Optional[str] = None

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

@app.post("/api/reminders")
def add_reminder_api(request: ReminderCreateRequest):

    try:
        reminder = create_reminder(request)

        return {
            "success": True,
            "message": "Reminder created successfully",
            "reminder": reminder
        }

    except ValueError as error:
        return {
            "success": False,
            "message": str(error)
        }

    except Exception as error:
        print("Create reminder API error:", error)

        return {
            "success": False,
            "message": "Unable to create reminder"
        }
    
@app.get("/api/reminders")
def list_reminders():

    try:
        reminders = fetch_all_reminders()

        return {
            "success": True,
            "reminders": reminders
        }

    except Exception as error:

        print("Get reminders error:", error)

        return {
            "success": False,
            "message": "Unable to load reminders",
            "reminders": []
        }

@app.delete("/api/reminders/{reminder_id}")
def delete_reminder_api(reminder_id: int):

    try:

        deleted = remove_reminder(reminder_id)

        if not deleted:
            return {
                "success": False,
                "message": "Reminder not found"
            }

        return {
            "success": True,
            "message": "Reminder deleted successfully"
        }

    except Exception as error:

        print(error)

        return {
            "success": False,
            "message": "Unable to delete reminder"
        }
    
@app.patch("/api/reminders/{reminder_id}/status")
def update_reminder_status_api(
    reminder_id: int,
    request: ReminderStatusRequest
):

    try:
        updated_status = change_reminder_status(
            reminder_id,
            request.is_active
        )

        if updated_status is None:
            return {
                "success": False,
                "message": "Reminder not found"
            }

        return {
            "success": True,
            "message": "Reminder status updated successfully",
            "is_active": updated_status
        }

    except Exception as error:

        print("Update reminder status error:", error)

        return {
            "success": False,
            "message": "Unable to update reminder status"
        }

@app.get("/api/whatsapp/recipients")
def list_whatsapp_recipients():

    try:
        recipients = get_whatsapp_recipients()

        return {
            "success": True,
            "contacts": recipients["contacts"],
            "groups": recipients["groups"],
        }

    except requests.RequestException as error:

        print(
            "WAHA recipient API error:",
            error
        )

        return {
            "success": False,
            "message": "Unable to load WhatsApp recipients",
            "contacts": [],
            "groups": [],
        }

    except Exception as error:

        print(
            "Recipient loading error:",
            error
        )

        return {
            "success": False,
            "message": str(error),
            "contacts": [],
            "groups": [],
        }

@app.post("/api/contacts")
def add_contact(request: SavedContactRequest):

    try:
        contact = create_saved_contact(request)

        return {
            "success": True,
            "message": "Contact saved successfully",
            "contact": contact
        }

    except ValueError as error:
        return {
            "success": False,
            "message": str(error)
        }

    except Exception as error:
        print("Create contact error:", error)

        return {
            "success": False,
            "message": "Unable to save contact"
        }

@app.get("/api/contacts")
def list_contacts():

    try:
        contacts = fetch_saved_contacts()

        return {
            "success": True,
            "contacts": contacts
        }

    except Exception as error:
        print("Load contacts error:", error)

        return {
            "success": False,
            "message": "Unable to load contacts",
            "contacts": []
        }

@app.delete("/api/contacts/{contact_id}")
def delete_contact(contact_id: int):

    try:
        deleted = remove_saved_contact(contact_id)

        if not deleted:
            return {
                "success": False,
                "message": "Contact not found"
            }

        return {
            "success": True,
            "message": "Contact deleted successfully"
        }

    except Exception as error:
        print("Delete contact error:", error)

        return {
            "success": False,
            "message": "Unable to delete contact"
        }

@app.post("/api/reports")
def add_report(request: ReminderReportRequest):

    try:
        report = create_report(request)

        return {
            "success": True,
            "message": "Report saved successfully",
            "report": report
        }

    except ValueError as error:
        return {
            "success": False,
            "message": str(error)
        }

    except Exception as error:
        print("Create report error:", error)

        return {
            "success": False,
            "message": "Unable to save report"
        }        

@app.get("/api/reports")
def list_reports():

    try:
        reports = fetch_reports()

        return {
            "success": True,
            "reports": reports
        }

    except Exception as error:
        print("Load reports error:", error)

        return {
            "success": False,
            "message": "Unable to load reports",
            "reports": []
        }

@app.put("/api/reports/{report_id}")
def update_report_api(
    report_id: int,
    request: ReminderReportRequest
):

    try:
        report = edit_report(
            report_id,
            request
        )

        if not report:
            return {
                "success": False,
                "message": "Report not found"
            }

        return {
            "success": True,
            "message": "Report updated successfully",
            "report": report
        }

    except ValueError as error:
        return {
            "success": False,
            "message": str(error)
        }

    except Exception as error:
        print("Update report error:", error)

        return {
            "success": False,
            "message": "Unable to update report"
        }

@app.delete("/api/reports/{report_id}")
def delete_report_api(report_id: int):

    try:
        deleted = remove_report(report_id)

        if not deleted:
            return {
                "success": False,
                "message": "Report not found"
            }

        return {
            "success": True,
            "message": "Report deleted successfully"
        }

    except ValueError as error:
        return {
            "success": False,
            "message": str(error)
        }

    except Exception as error:
        print("Delete report error:", error)

        return {
            "success": False,
            "message": "Unable to delete report"
        }






