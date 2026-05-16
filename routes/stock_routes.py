from fastapi import APIRouter, HTTPException
from models.stockModels import StockInput, StockResponse, StockSignals
from services.analyse_service import simple_sentiment, investment_decision
from services.analyse_claude import analyse_with_claude
from agents.multiagent import multiagent
from models.schema import parser, format_instructions

router = APIRouter()

@router.get("/fetch/alpha/{stock_symbol}")
def fetch_alpha_signals(stock_symbol: str):
    return fetch_news_sentiment_alpha(tickers=stock_symbol)

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
        result = multiagent.run(query)
        parsed = parser.parse(result)
        return parsed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {str(e)}")