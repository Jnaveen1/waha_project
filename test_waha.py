# from waha import get_all_chats, get_messages
# from service import save_message

# chats = get_all_chats()

# print("Total Chats:", len(chats))

# for chat in chats:

#     chat_id = chat["id"]["_serialized"]

#     chat_name = chat.get("name", "Unknown Chat")
#     print(f"\nChecking Chat: {chat_name}")

#     messages = get_messages(chat_id, limit=5)

#     for msg in messages:
#         save_message(msg)

import requests

response = requests.post(
    "http://127.0.0.1:8000/test-farm",
    json={
        "body": "Last week report in pdf."
    }
)

print(response.json())
