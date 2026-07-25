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
import time

from llm import understand_message


messages = [
    "Shed 1 has 5000 live birds",
    "10 birds died in shed 2",
    "Shed 3 consumed 75 kg feed",
    "Add 500 kg layer feed stock",
    "Remove 50 kg layer feed from stock",
    "Show feed stock",
    "Add 10 bottles of medicine A",
    "Remove 2 bottles of medicine A",
    "Show medicine stock",
]


for message in messages:
    print("\nMessage:", message)

    result = understand_message(message)

    print("Result:", result)

    time.sleep(5)