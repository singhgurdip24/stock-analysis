from langchain.tools import tool
from services.fetch_signals_yfinance import get_three_month_price_history

@tool
def stock_signal_tool(ticker: str) -> dict:
    """
    Analyze a stock ticker and return trend and RSI.
    Use this when the user asks about stock analysis, signals, or trends.
    """
    return get_three_month_price_history(ticker)