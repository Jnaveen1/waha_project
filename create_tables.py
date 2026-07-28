from database import engine, Base
import models

from models import FarmFinancialSetting, FeedPriceSetting 

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully!") 
