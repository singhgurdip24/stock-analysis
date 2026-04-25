import asyncio
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

def get_stock_signals(stock_symbol: str, retries: int = 3, delay: float = 5.0):
    ticker = yf.Ticker(stock_symbol)
    for attempt in range(retries):
        try:
            news = ticker.news
            print(f"Fetched news for {stock_symbol}: {news}")
            return news
        except YFRateLimitError:
            if attempt == retries - 1:
                raise
            asyncio.sleep(delay * (attempt + 1))
