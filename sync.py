import time

from waha import get_messages
from service import save_message

CHAT_ID = "120363406924564250@g.us"
while True:
    try:
        messages = get_messages(CHAT_ID, limit=20)

        # Oldest → Newest
        messages.reverse()

        for msg in messages:

            if msg["timestamp"] <= state.last_timestamp:
                continue

            save_message(msg)

            state.last_timestamp = msg["timestamp"]

        print("Waiting...")
        time.sleep(10)

    except Exception as e:
        print(e)
        time.sleep(10)