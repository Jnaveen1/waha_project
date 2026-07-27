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

from service import process_request

data = {
    "intent": "add_production",
    "shed": 1,
    "quantity": 100,
    "date": "today",
    "language": "en"
}

result = process_request(data)
print(result)

