from langchain.tools import tool
import yfinance as yf

@tool
def fundamentals_tool(ticker: str) -> dict:
    """
    Analyze company fundamentals like valuation and growth.
    Use when user asks about long-term investment or company health.
    """
    stock = yf.Ticker(ticker)
    info = stock.info

    pe_ratio       = info.get("trailingPE")
    revenue_growth = info.get("revenueGrowth")
    profit_margin  = info.get("profitMargins")
    debt_to_equity = info.get("debtToEquity")

    score = compute_fundamental_score(pe_ratio, revenue_growth, profit_margin, debt_to_equity)

    result = {
        "pe_ratio":             pe_ratio,
        "revenue_growth":       revenue_growth,
        "profit_margin":        profit_margin,
        "debt_to_equity":       debt_to_equity,
        "fundamental_score":    score,
    }
    print("Fundamentals result:", result)
    return result


def compute_fundamental_score(pe_ratio, revenue_growth, profit_margin, debt_to_equity) -> float:
    score = 0.5

    # PE ratio — lower is better (under 25 is healthy)
    if pe_ratio is not None:
        if pe_ratio < 15:
            score += 0.15
        elif pe_ratio < 25:
            score += 0.05
        else:
            score -= 0.10

    # Revenue growth — higher is better
    if revenue_growth is not None:
        if revenue_growth > 0.20:
            score += 0.15
        elif revenue_growth > 0.05:
            score += 0.05
        else:
            score -= 0.10

    # Profit margin — higher is better
    if profit_margin is not None:
        if profit_margin > 0.20:
            score += 0.15
        elif profit_margin > 0.05:
            score += 0.05
        else:
            score -= 0.10

    # Debt to equity — lower is better
    if debt_to_equity is not None:
        if debt_to_equity < 0.5:
            score += 0.05
        elif debt_to_equity > 2.0:
            score -= 0.10

    return round(max(0.0, min(score, 1.0)), 2)
