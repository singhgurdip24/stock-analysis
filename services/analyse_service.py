def simple_sentiment(text: str):
    positive_words = ["good", "growth", "profit", "up"]
    negative_words = ["loss", "bad", "down", "drop"]

    score = 0

    for word in positive_words:
        if word in text.lower():
            score += 1

    for word in negative_words:
        if word in text.lower():
            score -= 1

    if score > 0:
        return "positive"
    elif score < 0:
        return "negative"
    return "neutral"


def investment_decision(sentiment: str):
    if sentiment == "positive":
        return "BUY"
    elif sentiment == "negative":
        return "SELL"
    return "HOLD"