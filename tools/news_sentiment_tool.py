import yfinance as yf
from langchain.tools import tool
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage

llm = ChatAnthropic(model="claude-opus-4-7")

@tool
def news_sentiment_tool(ticker: str) -> dict:
    """
    Analyze recent news sentiment for a stock using Claude.
    Use when user asks about market sentiment or recent developments.
    """
    stock = yf.Ticker(ticker)
    news = stock.news

    if not news:
        return {"sentiment": "neutral", "headlines": []}

    headlines = [item['content']['title'] for item in news[:5]]
    headlines_text = "\n".join(f"- {h}" for h in headlines)

    response = llm.invoke([
        HumanMessage(content=(
            f"Classify the overall sentiment of these stock news headlines as "
            f"positive, negative, or neutral. Reply with one word only.\n\n{headlines_text}"
        ))
    ])

    sentiment = response.content.strip().lower()
    if sentiment not in ("positive", "negative", "neutral"):
        sentiment = "neutral"

    sentiment_score = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}[sentiment]

    result = {
        "sentiment": sentiment,
        "sentiment_score": sentiment_score,
        "headlines": headlines
    }
    print("News sentiment result:", result)
    return result
