from fastapi import APIRouter
from models.stockModels import StockInput, StockResponse
from services.analyse_service import simple_sentiment, investment_decision
from services.fetch_signals import get_stock_signals

router = APIRouter()

@router.get("/analyze/{stock_symbol}", response_model=StockResponse)
def analyze_stock(stock_symbol: str):
    signal = fetch_stock_signals(stock_symbol)
    sentiment = simple_sentiment(signal)
    decision = investment_decision(sentiment)

    return {
        "sentiment": sentiment,
        "decision": decision
    }

@router.get("/fetch/{stock_symbol}")
def fetch_stock_signals(stock_symbol: str):
    signals = get_stock_signals(stock_symbol)
    context_summary = ""
    for s in signals:
        text = s.get("content").get("summary")
        context_summary += text + " "
    return context_summary;