import requests
import time


WAHA_URL = "http://localhost:3000/api/sendText"
WAHA_SESSION = "default"
WAHA_API_KEY = "naveen123"


GROUPS = [
    "120363423099150354@g.us",
    "120363345095589925@g.us",
    "120363422507401551@g.us",
]


def send_reminder_to_recipient(
    chat_id: str,
    message: str
):
    headers = {
        "X-Api-Key": WAHA_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "session": WAHA_SESSION,
        "chatId": chat_id,
        "text": message,
    }

    last_error = None

    for attempt in range(2):
        try:
            response = requests.post(
                WAHA_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )

            return {
                "chat_id": chat_id,
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response": response.text,
            }

        except requests.Timeout as error:
            last_error = error

            print(
                f"WAHA timeout for {chat_id}. "
                f"Attempt {attempt + 1}/2"
            )

            if attempt == 0:
                time.sleep(5)

        except requests.RequestException as error:
            return {
                "chat_id": chat_id,
                "success": False,
                "error": str(error),
            }

    return {
        "chat_id": chat_id,
        "success": False,
        "error": str(last_error),
    }
    
def get_whatsapp_recipients():

    headers = {
        "X-Api-Key": WAHA_API_KEY,
    }

    response = requests.get(
        f"http://localhost:3000/api/{WAHA_SESSION}/chats",
        headers=headers,
        params={
            "limit": 1000,
            "offset": 0,
        },
        timeout=60,
    )

    response.raise_for_status()

    chats = response.json()

    contacts = []
    groups = []

    for chat in chats:

        chat_id = (
            chat.get("id")
            or chat.get("chatId")
        )

        if isinstance(chat_id, dict):
            chat_id = (
                chat_id.get("_serialized")
                or chat_id.get("serialized")
            )

        if not chat_id:
            continue

        chat_name = (
            chat.get("name")
            or chat.get("pushname")
            or chat.get("formattedTitle")
            or chat.get("displayName")
            or chat_id
        )

        recipient = {
            "recipient_name": chat_name,
            "chat_id": chat_id,
        }

        if chat_id.endswith("@g.us"):

            recipient["recipient_type"] = "group"

            groups.append(recipient)

        elif (
            chat_id.endswith("@c.us")
            or chat_id.endswith("@lid")
        ):

            recipient["recipient_type"] = "contact"

            contacts.append(recipient)

    contacts.sort(
        key=lambda item: item["recipient_name"].lower()
    )

    groups.sort(
        key=lambda item: item["recipient_name"].lower()
    )

    return {
        "contacts": contacts,
        "groups": groups,
    }