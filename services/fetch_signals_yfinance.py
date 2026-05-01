import pandas as pd
import numpy as np
import yfinance as yf
from models.stockModels import StockSignals

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

def get_stock_signals(stock_symbol: str):
    ticker = yf.Ticker(stock_symbol)
    news = ticker.news
    print(f"Fetched news for {stock_symbol}: {news}")
    return news

def get_three_month_price_history(stock_symbol: str):
    if STUB:
        df = _stub_download(stock_symbol, period="3mo")
    else:
        df = yf.download(stock_symbol, period="3mo", progress=False, auto_adjust=False)

    if df.empty:
        raise ValueError(f"No data found for symbol: {stock_symbol}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df['ma20'] = df['Close'].rolling(window=20).mean().round(2)
    df['ma50'] = df['Close'].rolling(window=50).mean().round(2)

    df['trend'] = df.apply(get_trend, axis=1)
    df['rsi'] = calc_rsi_series(df['Close'])
    df['rsi_signal'] = df['rsi'].apply(interpret_rsi)
    rsi_signal = df['rsi_signal'].iloc[-1]
    rsi = round(float(df['rsi'].iloc[-1]), 2)
    trend = df['trend'].iloc[-1]
    technical_confidence = compute_confidence(trend,rsi)

    return StockSignals(trend=trend, rsi=rsi, rsi_signal=rsi_signal, technical_confidence=technical_confidence)

def compute_confidence(trend, rsi):
    score = 0.5

    if trend == "bullish":
        score += 0.2
    else:
        score -= 0.2

    if rsi > 70 or rsi < 30:
        score -= 0.1  # risky zone

    return max(0, min(score, 1))

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
