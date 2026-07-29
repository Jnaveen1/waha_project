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

# import requests

# url = "http://127.0.0.1:8000/test-farm"

# payload = {
#     "body": "give me today financial reprot in pdf ."
# }

# response = requests.post(url, json=payload)

# print("Status code:", response.status_code)
# print("Raw response:", response.text)

# try:
#     print("JSON response:", response.json())
# except Exception as error:
#     print("Response is not JSON:", error)



# from database import confirm_customer_order
# order = confirm_customer_order(
#     "919876543210@c.us"
# )

# print(order.status)
# print(order.confirmed_at)


import requests

url = "http://127.0.0.1:8000/test-farm"

message = {
    "message": "Reminder: Please send today's farm production, feed, mortality and sales details."
}

response = requests.post(
    url,
    json=message,
    timeout=30,
)

print("Status code:", response.status_code)
print("Response:", response.text)


