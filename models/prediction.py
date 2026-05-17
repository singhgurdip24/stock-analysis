from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base
from datetime import datetime

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)

    ticker = Column(String)

    short_term = Column(String)
    medium_term = Column(String)
    long_term = Column(String)

    confidence = Column(Float)

    price_at_prediction = Column(Float)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Filled later
    actual_price = Column(Float, nullable=True)

    evaluation_result = Column(String, nullable=True)