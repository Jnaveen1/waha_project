from database import SessionLocal
from models import Message
from waha import get_phone_number_from_lid


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
        from_me = msg.get("fromMe", False)

        if from_me:
            sender_id = from_id
        else:
            sender_id = msg.get("participant") or from_id

        sender_phone = get_phone_number_from_lid(sender_id)
        sender_name = message_data.get("notifyName")

        new_message = Message(
            message_id=message_id,
            chat_id=from_id,
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
        print("Sender:", sender_phone)
        print("WhatsApp name:", sender_name)

    except Exception as error:
        db.rollback()
        print("Error saving message:", error)

    finally:
        db.close()