import requests

BASE_URL = "http://localhost:3000"
API_KEY = "naveen123"

HEADERS = {
    "X-Api-Key": API_KEY
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

    print("Calling URL:", response.url)
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
            print("LID response:", data)

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
