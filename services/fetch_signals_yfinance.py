import asyncio
import pandas as pd
import numpy as np
import yfinance as yf
from yfinance.exceptions import YFRateLimitError

STUB = True  # set to False to use real yfinance data

def _stub_download(stock_symbol: str, period: str) -> pd.DataFrame:
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=63)  # 63 trading days ≈ 3 months
    np.random.seed(42)
    close = 150 + np.cumsum(np.random.randn(63))  # random walk starting at $150
    df = pd.DataFrame({
        ('Open',      stock_symbol): close - np.random.uniform(0, 1, 63),
        ('High',      stock_symbol): close + np.random.uniform(0, 2, 63),
        ('Low',       stock_symbol): close - np.random.uniform(0, 2, 63),
        ('Close',     stock_symbol): close,
        ('Adj Close', stock_symbol): close,
        ('Volume',    stock_symbol): np.random.randint(30_000_000, 60_000_000, 63),
    }, index=dates)
    df.columns = pd.MultiIndex.from_tuples(df.columns, names=['Price', 'Ticker'])
    return df

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

def get_three_month_price_history(stock_symbol: str):
    df = _stub_download(stock_symbol, period="3mo") if STUB else yf.download(stock_symbol, period="3mo")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df['ma20'] = df['Close'].rolling(window=20).mean().round(2)
    df['ma50'] = df['Close'].rolling(window=50).mean().round(2)

    x = df.iloc[-1]
    for element in x:
        print (element)

    print("ma20: ", round(float(x['ma20']), 2))
    print("ma50: ", round(float(x['ma50']), 2))
        
    return get_trend(x)

def get_trend(row):
    x = round(float(row['ma20']), 2)
    y = round(float(row['ma50']), 2)
    if x > y:
        return "bullish"
    elif x < y:
        return "bearish"
    else:
        return "sideways"