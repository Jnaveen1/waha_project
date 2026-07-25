from database import SessionLocal
from models import Message
from llm import generate_friend_reply
from waha import (
    get_phone_number_from_lid,
    get_chat_name,
    send_message
)

ALLOWED_GROUP_ID = "120363423099150354@g.us"

def save_message(msg):
    db = SessionLocal()

    try:
        message_id = msg.get("id")

        if not message_id:
            print("Message ignored: message ID missing")
            return

        existing = (
            db.query(Message)
            .filter(Message.message_id == message_id)
            .first()
        )

        if existing:
            print("Message already exists")
            return

        message_data = msg.get("_data", {})

        from_id = msg.get("from", "")
        to_id = msg.get("to", "")
        from_me = msg.get("fromMe", False)

        # Find the actual conversation ID
        if from_me:
            chat_id = to_id
        else:
            chat_id = from_id

        # Check whether this conversation is a group
        is_group = chat_id.endswith("@g.us")

        # Get personal contact name or group name
        chat_name = get_chat_name(chat_id)

        # Find the actual sender
        if from_me:
            sender_id = from_id
        else:
            sender_id = msg.get("participant") or from_id

        sender_phone = get_phone_number_from_lid(sender_id)
        sender_name = message_data.get("notifyName")

        new_message = Message(
            message_id=message_id,
            chat_id=chat_id,
            chat_name=chat_name,
            is_group=is_group,
            sender=sender_phone,
            sender_name=sender_name,
            from_me=from_me,
            body=msg.get("body", ""),
            timestamp=msg.get("timestamp"),
            message_type=message_data.get("type", "unknown")
        )

        db.add(new_message)
        db.commit()

        print("Message saved to MySQL")
        print("WhatsApp name:", sender_name)
        print("Chat name:", chat_name)
        print("Is group:", is_group)

        # Reply only to messages sent by another person inside a group
        if (
            is_group
            and not from_me
            and chat_id == ALLOWED_GROUP_ID
        ):

            message_body = msg.get("body", "")

            print("Friend:", message_body)

            reply_text = generate_friend_reply(message_body)

            print("LLM Reply:", reply_text)

            send_message(
                chat_id=chat_id,
                text=reply_text
            )

    except Exception as error:
        db.rollback()
        print("Error saving message:", error)

    finally:
        db.close()