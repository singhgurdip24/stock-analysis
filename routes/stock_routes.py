from fastapi import APIRouter, HTTPException
from models.stockModels import StockInput, StockResponse, StockSignals
from services.analyse_service import simple_sentiment, investment_decision
from services.analyse_claude import analyse_with_claude
from services.fetch_signals_alpha import fetch_news_sentiment_alpha
from services.fetch_signals_yfinance import get_stock_signals, get_three_month_price_history

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

@router.get("/fetch/alpha/{stock_symbol}")
def fetch_alpha_signals(stock_symbol: str):
    return fetch_news_sentiment_alpha(tickers=stock_symbol)

@router.get("/fetch/yahoo/{stock_symbol}")
def fetch_yahoo_signals(stock_symbol: str):
    return get_stock_signals(stock_symbol)

@router.get("/fetch/yahoo/history/{stock_symbol}", response_model=StockSignals)
def fetch_three_month_price_history(stock_symbol: str):
    try:
        return get_three_month_price_history(stock_symbol)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analyse/claude/{stock_symbol}")
def analyse_stock_claude(stock_symbol: str):
    try:
        signals = get_three_month_price_history(stock_symbol)
        return analyse_with_claude(signals)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

