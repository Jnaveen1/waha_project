import os
import requests
import time
from dotenv import load_dotenv
load_dotenv()

WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://localhost:3000")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "naveen123")
WAHA_URL = f"{WAHA_BASE_URL}/api/sendText"


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
        "X-Api-Key": WAHA_API_KEY
    }
    try:
        chats_data = []
        # Fetch active chats using limit=50 to avoid WAHA WEBJS engine timeouts
        for limit_val in [50, 40, 30]:
            try:
                response = requests.get(
                    f"{WAHA_BASE_URL}/api/{WAHA_SESSION}/chats",
                    headers=headers,
                    params={
                        "limit": limit_val
                    },
                    timeout=20
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        chats_data = data
                        break
            except requests.RequestException as req_err:
                print(
                    f"WAHA chats fetch attempt with limit={limit_val} failed:",
                    req_err
                )
        if not chats_data:
            return {
                "success": True,
                "contacts": [],
                "groups": []
            }
        groups = []
        seen_chat_ids = set()
        for chat in chats_data:
            chat_id = chat.get("id")
            if isinstance(chat_id, dict):
                chat_id = (
                    chat_id.get("_serialized")
                    or chat_id.get("user")
                    or chat_id.get("serialized")
                )
            elif not isinstance(chat_id, str):
                chat_id = str(chat_id) if chat_id else ""
            if not chat_id or chat_id in seen_chat_ids:
                continue
            # Filter ONLY WhatsApp group chats (@g.us)
            is_group = (
                chat_id.endswith("@g.us")
                or chat.get("isGroup") is True
                or bool(chat.get("groupMetadata"))
            )
            if not is_group:
                continue
            seen_chat_ids.add(chat_id)
            group_name = (
                chat.get("name")
                or chat.get("subject")
                or (chat.get("groupMetadata") or {}).get("subject")
                or chat.get("formattedTitle")
                or chat_id
            )
            groups.append({
                "recipient_name": group_name,
                "chat_id": chat_id,
                "recipient_type": "group"
            })
        groups.sort(
            key=lambda item: item["recipient_name"].lower()
        )
        return {
            "success": True,
            "contacts": [],
            "groups": groups
        }
    except requests.RequestException as error:
        print(
            "WAHA group API error:",
            error
        )
        return {
            "success": False,
            "message": (
                "Unable to load WhatsApp groups"
            ),
            "contacts": [],
            "groups": []
        }
    except Exception as error:
        print(
            "WAHA group parsing error:",
            error
        )
        return {
            "success": False,
            "message": (
                "Unable to process WhatsApp groups"
            ),
            "contacts": [],
            "groups": []
        }
