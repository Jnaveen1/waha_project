import requests
from urllib.parse import quote

BASE_URL = "http://localhost:3000"
API_KEY = "naveen123"

HEADERS = {
    "X-Api-Key": API_KEY , 
    "Content-Type": "application/json"
}


def get_session():
    response = requests.get(
        f"{BASE_URL}/api/sessions/default",
        headers=HEADERS
    )

    response.raise_for_status()
    return response.json()

def get_chats():
    response = requests.get(
        f"{BASE_URL}/api/default/chats",
        headers=HEADERS
    )

    response.raise_for_status()
    return response.json()

def get_messages(chat_id, limit=5):
    url = f"{BASE_URL}/api/default/chats/{chat_id}/messages"

    response = requests.get(
        url,
        headers=HEADERS,
        params={
            "limit": limit,
            "downloadMedia": False,
            "merge": True
        }
    )

    # print("Calling URL:", response.url)
    print("Status Code:", response.status_code)

    response.raise_for_status()
    return response.json()

def get_all_chats():
    url = f"{BASE_URL}/api/default/chats"

    response = requests.get(
        url,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.json()

def get_phone_number_from_lid(lid):
    if not lid or not lid.endswith("@lid"):
        return lid

    url = f"{BASE_URL}/api/default/lids/{lid}"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            # print("LID response:", data)

            return (
                data.get("pn")
                or data.get("phoneNumber")
                or data.get("phone_number")
                or lid
            )

        print("Could not resolve LID:", response.status_code)
        return lid

    except requests.RequestException as error:
        print("LID lookup error:", error)
        return lid

def get_chat_name(chat_id):
    if not chat_id:
        return None

    # Group chat
    if chat_id.endswith("@g.us"):
        encoded_chat_id = quote(chat_id, safe="")

        url = f"{BASE_URL}/api/default/groups/{encoded_chat_id}"

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10
            )

            # print("Group API status:", response.status_code)

            if response.status_code != 200:
                print("Group lookup failed:", response.text)
                return None

            group_data = response.json()

            return (
                group_data.get("subject")
                or group_data.get("name")
                or group_data.get("title")
            )

        except requests.RequestException as error:
            print("Group lookup error:", error)
            return None

    # Personal chat
    return get_contact_name(chat_id)

def get_contact_name(chat_id):
    if not chat_id:
        return None

    lookup_id = get_phone_number_from_lid(chat_id)

    url = f"{BASE_URL}/api/contacts"

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params={
                "session": "default",
                "contactId": lookup_id
            },
            timeout=10
        )

        # print("Contact API URL:", response.url)
        # print("Contact API status:", response.status_code)
        # print("Contact API response:", response.text)

        if response.status_code != 200:
            return None

        contact_data = response.json()

        return (
            contact_data.get("name")
            or contact_data.get("pushName")
            or contact_data.get("pushname")
            or contact_data.get("shortName")
        )

    except requests.RequestException as error:
        print("Contact lookup error:", error)
        return None

def send_message(chat_id, text):
    if not chat_id:
        print("Cannot send message: chat ID missing")
        return None

    if not text:
        print("Cannot send message: text missing")
        return None

    url = f"{BASE_URL}/api/sendText"

    payload = {
        "session": "default",
        "chatId": chat_id,
        "text": text
    }

    try:
        response = requests.post(
            url,
            headers=HEADERS,
            json=payload,
            timeout=10
        )

        print("Send message URL:", response.url)
        print("Send message status:", response.status_code)
        print("Send message response:", response.text)

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        print("Error sending WhatsApp message:", error)
        return None
    