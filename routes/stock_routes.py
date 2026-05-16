from fastapi import APIRouter, HTTPException
from models.stockModels import StockSignals
from services.analyse_claude import analyse_with_claude
from services.fetch_signals_alpha import fetch_news_sentiment_alpha, get_three_month_price_history
from agents.stock_analysis_agent import agent
from models.schema import parser, format_instructions

router = APIRouter()

@router.get("/fetch/alpha/{stock_symbol}")
def fetch_alpha_signals(stock_symbol: str):
    return fetch_news_sentiment_alpha(tickers=stock_symbol)


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

@router.get("/analyse/agent/{ticker}")
def analyse_stock_agent(ticker: str):
    query = f"""Analyze {ticker} stock.

    Give:
    - short term outlook
    - medium term outlook
    - long term outlook
    - reasoning based on trend, sentiment, and fundamentals

    Use:
    - technical_confidence
    - sentiment_score
    - fundamental_score

    Rules:
    - Combine these scores into a final confidence (0 to 1)
    - Do NOT invent values—base it on provided signals

    {format_instructions}
    """

    try:
        result = agent.run(query)
        parsed = parser.parse(result)
        return parsed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {str(e)}")