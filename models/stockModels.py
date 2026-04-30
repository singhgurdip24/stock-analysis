from pydantic import BaseModel

class StockInput(BaseModel):
    text: str

class StockResponse(BaseModel):
    sentiment: str
    decision: str

class StockSignals(BaseModel):
    trend: str
    rsi: float
    rsi_signal: str