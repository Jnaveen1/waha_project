from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Text, DateTime, Date,Time, ForeignKey, Float 
from base import Base
from datetime import datetime
from sqlalchemy.orm import relationship


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

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    report_id = Column(
        Integer,
        ForeignKey("reminder_reports.id"),
        nullable=False
    )

    message = Column(
        String(1000),
        nullable=False
    )

    repeat_type = Column(
        String(20),
        nullable=False
    )

    schedule_date = Column(
        Date,
        nullable=True
    )

    schedule_time = Column(
        Time,
        nullable=False
    )

    week_day = Column(
        String(20),
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    job_id = Column(
        String(100),
        unique=True,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    report = relationship(
        "ReminderReport",
        back_populates="reminders"
    )

    recipients = relationship(
        "ReminderRecipient",
        back_populates="reminder",
        cascade="all, delete-orphan"
    )

    status = Column(
        String(20),
        default="active",
        nullable=False
    )
   
class ReminderRecipient(Base):
    __tablename__ = "reminder_recipients"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    reminder_id = Column(
        Integer,
        ForeignKey(
            "reminders.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    recipient_name = Column(
        String(255),
        nullable=False
    )

    chat_id = Column(
        String(255),
        nullable=False
    )

    recipient_type = Column(
        String(20),
        nullable=False
    )

    reminder = relationship(
        "Reminder",
        back_populates="recipients"
    )

class SavedContact(Base):
    __tablename__ = "saved_contacts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    whatsapp_number = Column(
        String(30),
        nullable=False,
        unique=True
    )

    chat_id = Column(
        String(255),
        nullable=False,
        unique=True
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

class ReminderReport(Base):
    __tablename__ = "reminder_reports"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    report_name = Column(
        String(255),
        nullable=False
    )

    task_title = Column(
        String(255),
        nullable=False
    )

    message = Column(
        Text,
        nullable=False
    )

    details = Column(
        Text,
        nullable=True
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    reminders = relationship(
        "Reminder",
        back_populates="report"
    )
