from pydantic import BaseModel

class StockInput(BaseModel):
    text: str

class StockResponse(BaseModel):
    sentiment: str
    decision: str