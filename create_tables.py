from database import engine, Base
import models

from models import Message, EggRecord, FeedStock, MedicineStock

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully!") 