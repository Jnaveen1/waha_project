from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, DateTime
from database import Base
from datetime import datetime


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    message_id = Column(String(255), unique=True, nullable=False)
    chat_id = Column(String(255), nullable=False)

    sender = Column(String(255))
    sender_name = Column(String(255))

    from_me = Column(Boolean, default=False)
    body = Column(Text)
    timestamp = Column(BigInteger)
    message_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

    chat_name = Column(String(255), nullable=True)
    is_group = Column(Boolean, default=False)