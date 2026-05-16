import os
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from models.stockModels import StockSignals

load_dotenv()

_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY')
if not _API_KEY:
    raise EnvironmentError("ALPHA_VANTAGE_API_KEY is not set. Add it to your .env file.")
BASE_URL = 'https://www.alphavantage.co/query'

STUB = False  # set to False to use real Alpha Vantage data

def _stub_download(stock_symbol: str) -> pd.DataFrame:
    dates = pd.bdate_range(end=pd.Timestamp.today(), periods=63)
    np.random.seed(42)
    close = 150 + np.cumsum(np.random.randn(63))
    return pd.DataFrame({
        'Open':   close - np.random.uniform(0, 1, 63),
        'High':   close + np.random.uniform(0, 2, 63),
        'Low':    close - np.random.uniform(0, 2, 63),
        'Close':  close,
        'Volume': np.random.randint(30_000_000, 60_000_000, 63),
    }, index=dates)

def _fetch_from_alpha(stock_symbol: str) -> pd.DataFrame:
    params = {
        'function':   'TIME_SERIES_DAILY',
        'symbol':     stock_symbol,
        'outputsize': 'compact',  # last 100 trading days — enough for 3mo + MA50
        'apikey':     _API_KEY,
    }
    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    data = r.json()

    if 'Time Series (Daily)' not in data:
        raise ValueError(data.get('Error Message') or data.get('Note') or data.get('Information') or f"No data for {stock_symbol}")

    series = data['Time Series (Daily)']
    df = pd.DataFrame.from_dict(series, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    df = df.rename(columns={
        '1. open':   'Open',
        '2. high':   'High',
        '3. low':    'Low',
        '4. close':  'Close',
        '5. volume': 'Volume',
    })
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)

    # keep last 63 trading days (~3 months)
    return df.tail(63)

def get_three_month_price_history(stock_symbol: str):
    df = _stub_download(stock_symbol) if STUB else _fetch_from_alpha(stock_symbol)

    if df.empty:
        raise ValueError(f"No data found for symbol: {stock_symbol}")

    df['ma20'] = df['Close'].rolling(window=20).mean().round(2)
    df['ma50'] = df['Close'].rolling(window=50).mean().round(2)
    df['trend'] = df.apply(get_trend, axis=1)
    df['rsi'] = calc_rsi_series(df['Close'])
    df['rsi_signal'] = df['rsi'].apply(interpret_rsi)
    rsi_signal = df['rsi_signal'].iloc[-1]
    rsi = round(float(df['rsi'].iloc[-1]), 2)
    trend = df['trend'].iloc[-1]
    technical_confidence = compute_confidence(trend, rsi)

    return StockSignals(trend=trend, rsi=rsi, rsi_signal=rsi_signal, technical_confidence=technical_confidence)

def compute_confidence(trend, rsi):
    score = 0.5
    if trend == "bullish":
        score += 0.2
    else:
        score -= 0.2
    if rsi > 70 or rsi < 30:
        score -= 0.1
    return round(max(0, min(score, 1)), 2)

def get_trend(x):
    ma20 = x['ma20']
    ma50 = x['ma50']
    if ma20 > ma50:
        return "bullish"
    elif ma20 < ma50:
        return "bearish"
    else:
        return "sideways"

def calc_rsi_series(close: pd.Series) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    return (100 - (100 / (1 + rs))).round(2)

def interpret_rsi(rsi):
    if rsi > 70:
        return "overbought"
    elif rsi < 30:
        return "oversold"
    else:
        return "neutral"
