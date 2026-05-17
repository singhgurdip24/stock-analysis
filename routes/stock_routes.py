from fastapi import APIRouter, HTTPException
from agents.multiagent import multiagent
from models.schema import parser, format_instructions
from services.fetch_signals_alpha import fetch_news_sentiment_alpha
from database import SessionLocal
from models.prediction import Prediction

router = APIRouter()

@router.get("/fetch/alpha/{stock_symbol}")
def fetch_alpha_signals(stock_symbol: str):
    return fetch_news_sentiment_alpha(tickers=stock_symbol)

@router.get("/predictions")
def get_predictions():

    db = SessionLocal()
    predictions = db.query(Prediction).all()
    return predictions

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

        db = SessionLocal()
        try:
            prediction = Prediction(
                ticker=ticker.upper(),
                short_term=parsed.get("short_term"),
                medium_term=parsed.get("medium_term"),
                long_term=parsed.get("long_term"),
                confidence=parsed.get("confidence"),
                price_at_prediction=parsed.get("current_price"),
            )
            db.add(prediction)
            db.commit()
            db.refresh(prediction)
            parsed["prediction_id"] = prediction.id
        finally:
            db.close()

        return parsed
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Analysis failed: {str(e)}")