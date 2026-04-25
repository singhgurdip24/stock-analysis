import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = 'https://www.alphavantage.co/query'
_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')

def fetch_news_sentiment_alpha(tickers: str, apikey: str = _API_KEY, **kwargs) -> dict:
    params = {
        'function': 'NEWS_SENTIMENT',
        'tickers': tickers,
        'apikey': apikey,
        **kwargs,
    }
    r = requests.get(BASE_URL, params=params)
    r.raise_for_status()
    return r.json()
