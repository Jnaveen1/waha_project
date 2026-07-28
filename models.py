from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, DateTime, Date, Float 
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
    first_collection = Column(Integer, default=0)
    second_collection = Column(Integer, default=0)
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

class EggPriceSetting(Base):
    __tablename__ = "egg_price_settings"

    id = Column(Integer, primary_key=True, index=True)

    price_per_egg = Column(Float, nullable=False)
    eggs_per_tray = Column(Integer, nullable=False)
    price_per_tray = Column(Float, nullable=False)

    discount_threshold = Column(Integer, nullable=False)
    discount_percentage = Column(Float, nullable=False)

    available_eggs = Column(Integer, nullable=False, default=0)

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

class CustomerOrder(Base):
    __tablename__ = "customer_orders"

    id = Column(Integer, primary_key=True, index=True)

    chat_id = Column(String(150), nullable=False)
    customer_whatsapp = Column(String(30), nullable=False)

    quantity_eggs = Column(Integer, nullable=False)

    subtotal = Column(Float, nullable=False)
    discount_percentage = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)

    status = Column(String(20), default="pending")

    created_at = Column(DateTime, default=datetime.now)
    confirmed_at = Column(DateTime, nullable=True)

class FarmFinancialSetting(Base):

    __tablename__ = "farm_financial_settings"

    id = Column(Integer, primary_key=True, index=True)

    egg_price = Column(Float, nullable=False)

    expected_percentage = Column(Float, default=95.0)

    effective_date = Column(Date, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )

class FeedPriceSetting(Base):

    __tablename__ = "feed_price_settings"

    id = Column(Integer, primary_key=True, index=True)

    feed_name = Column(String(100), nullable=False)

    cost_per_ton = Column(Float, nullable=False)

    effective_date = Column(Date, nullable=False)

    updated_at = Column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now
    )