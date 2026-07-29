import requests


WAHA_URL = "http://localhost:3000/api/sendText"
WAHA_SESSION = "default"
WAHA_API_KEY = "naveen123"


GROUPS = [
    "120363423099150354@g.us",
    "120363345095589925@g.us",
    "120363422507401551@g.us",
]


def send_reminder_to_all_groups(message: str):

    results = []

    headers = {
        "X-Api-Key": WAHA_API_KEY,
        "Content-Type": "application/json",
    }

    for chat_id in GROUPS:

        payload = {
            "session": WAHA_SESSION,
            "chatId": chat_id,
            "text": message,
        }

        try:
            response = requests.post(
                WAHA_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )

            results.append({
                "chat_id": chat_id,
                "status_code": response.status_code,
                "success": response.status_code in [200, 201],
                "response": response.text,
            })

        except requests.RequestException as error:
            results.append({
                "chat_id": chat_id,
                "success": False,
                "error": str(error),
            })

    return results