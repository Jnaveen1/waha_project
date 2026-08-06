from database import engine, Base
import models

import models 

print("Creating database tables...")

Base.metadata.create_all(bind=engine)

print("Tables Created Successfully!") 



