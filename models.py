from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, DateTime, Float 
from base import Base
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



class EggRecord(Base):

    __tablename__ = "egg_records"

    id = Column(Integer, primary_key=True)

    date = Column(String(20))
    shed_no = Column(Integer)
    birds = Column(Integer, nullable=True)
    mortality = Column(Integer, nullable=True)
    produced = Column(Integer, nullable=True)
    broken = Column(Integer, nullable=True)
    sold = Column(Integer, nullable=True)


class MedicineStock(Base):

    __tablename__ = "medicine_stock"

    id = Column(Integer, primary_key=True)

    shed_no = Column(Integer, nullable=False)
    medicine_name = Column(String(100), nullable=False)
    available = Column(Float, default=0)
    used = Column(Float, default=0)
    unit = Column(String(20), default="ml")


class FeedStock(Base):

    __tablename__ = "feed_stock"

    id = Column(Integer, primary_key=True)

    date = Column(String(20), nullable=False)
    shed_no = Column(Integer, nullable=False)
    feed_name = Column(String(100), nullable=False)
    available = Column(Float, default=0)
    used = Column(Float, default=0)
    unit = Column(String(20), default="kg")

