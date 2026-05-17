from database import engine
from database import Base
from models.prediction import Prediction

Base.metadata.create_all(bind=engine)

print("Database tables created!")