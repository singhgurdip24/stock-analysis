# Stock Analysis API

A FastAPI application that performs AI-powered stock analysis using a multi-agent architecture. It combines **technical signals**, **news sentiment**, and **fundamental data** — all sourced from Alpha Vantage — and synthesises them into a structured investment outlook via a LangChain ReAct agent powered by Claude Opus.

---

## Features

- **Multi-agent analysis** — A ReAct agent autonomously decides which tools to call and combines their outputs into a final recommendation.
- **Technical signals** — MA20/MA50 crossover trend detection and 14-period RSI with confidence scoring.
- **News sentiment** — Top-5 recent headlines classified as positive/negative/neutral by Claude.
- **Fundamental scoring** — PE ratio, revenue growth, profit margin, and debt-to-equity scored on a 0–1 scale.
- **Structured output** — Response is parsed into typed fields (short/medium/long-term outlook, confidence, reasons, risks).

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | [FastAPI](https://fastapi.tiangolo.com/) |
| AI orchestration | [LangChain](https://www.langchain.com/) (ReAct agent) |
| LLM | [Claude Opus 4.7](https://www.anthropic.com/) via `langchain-anthropic` |
| Market data | [Alpha Vantage](https://www.alphavantage.co/) REST API |
| Output parsing | `langchain-classic` `StructuredOutputParser` |

---

## Project Structure

```
stock-analysis/
├── main.py                        # FastAPI app entry point
├── .env.example                   # Environment variable template
│
├── agents/
│   └── multiagent.py              # LangChain ReAct agent with 3 tools
│
├── routes/
│   └── stock_routes.py            # API route definitions
│
├── tools/
│   ├── stock_signal_tool.py       # Technical analysis tool (trend + RSI)
│   ├── news_sentiment_tool.py     # News sentiment tool (Claude-powered)
│   └── fundamentals_tool.py      # Fundamental scoring tool
│
├── services/
│   ├── fetch_signals_alpha.py     # Alpha Vantage API client + signal computation
│   ├── analyse_claude.py          # Direct Claude analysis (non-agent endpoint)
│   └── analyse_service.py        # Simple keyword-based sentiment (legacy)
│
└── models/
    ├── schema.py                  # StructuredOutputParser schema
    └── stockModels.py             # Pydantic models
```

---

## Setup

### Prerequisites

- Python 3.10+
- An [Alpha Vantage API key](https://www.alphavantage.co/support/#api-key) (free tier available)
- An [Anthropic API key](https://console.anthropic.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/singhgurdip24/stock-analysis.git
cd stock-analysis

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn langchain langchain-anthropic langchain-classic \
            anthropic requests pandas numpy python-dotenv
```

### Environment Variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

---

## API Endpoints

<!-- ENDPOINT_INDEX_START -->
| Method | Path | Handler |
|--------|------|---------|
| `GET` | `/fetch/alpha/{stock_symbol}` | `fetch_alpha_signals` |
| `GET` | `/fetch/test-hook/{stock_symbol}` | `fetch_alpha_signals` |
| `GET` | `/analyse/agent/{ticker}` | `analyse_stock_agent` |
<!-- ENDPOINT_INDEX_END -->


### `GET /analyse/agent/{ticker}`

**The primary endpoint.** Runs the multi-agent analysis pipeline and returns a structured investment outlook.

**Example request:**
```bash
curl http://127.0.0.1:8000/analyse/agent/AAPL
```

**Example response:**
```json
{
  "short_term": "bullish",
  "medium_term": "neutral",
  "long_term": "bullish",
  "confidence": 0.72,
  "reasons": [
    "MA20 above MA50 confirms upward momentum",
    "RSI at 58 — not overbought",
    "Positive news sentiment from recent headlines"
  ],
  "risks": [
    "Macro headwinds could compress margins",
    "High PE ratio relative to sector peers"
  ],
  "uncertainties": [
    "Upcoming earnings report may shift sentiment"
  ],
  "assumptions": [
    "Current trend continues without major market disruption"
  ],
  "analysis": "Full analysis text from the agent..."
}
```

---

### `GET /fetch/alpha/{stock_symbol}`

Fetches raw news sentiment data from Alpha Vantage for a given ticker.

```bash
curl http://127.0.0.1:8000/fetch/alpha/TSLA
```

---

### `GET /fetch/yahoo/history/{stock_symbol}`

Returns the latest technical signals for a ticker (trend, RSI, confidence).

```bash
curl http://127.0.0.1:8000/fetch/yahoo/history/MSFT
```

**Response:**
```json
{
  "trend": "bullish",
  "rsi": 62.4,
  "rsi_signal": "neutral",
  "technical_confidence": 0.7
}
```

---

## How the Agent Works

The `/analyse/agent/{ticker}` endpoint uses a **LangChain ReAct (Reason + Act)** agent. On each request, the agent autonomously loops through:

1. **Thought** — decides what information it needs next
2. **Action** — calls one of its three tools
3. **Observation** — reads the tool's output
4. Repeats until it has enough data, then produces a final structured answer

```
GET /analyse/agent/{ticker}
         │
         ▼
  Build natural-language query with format instructions
         │
         ▼
  ReAct Agent (Claude Opus 4.7)
         │
         ├──► stock_signal_tool       MA20/MA50 trend + RSI + technical_confidence
         │         └── Alpha Vantage TIME_SERIES_DAILY
         │
         ├──► news_sentiment_tool     Top-5 headlines → Claude classifies sentiment
         │         └── Alpha Vantage NEWS_SENTIMENT + inner Claude call
         │
         └──► fundamentals_tool       PE, growth, margin, D/E → fundamental_score
                   └── Alpha Vantage OVERVIEW
         │
         ▼
  Agent synthesises all three scores into outlook + confidence
         │
         ▼
  StructuredOutputParser → typed JSON response
```

### Scoring Summary

| Signal | Source | Range |
|---|---|---|
| `technical_confidence` | MA crossover + RSI | 0.0 – 1.0 |
| `sentiment_score` | Claude headline classification | 0.0 / 0.5 / 1.0 |
| `fundamental_score` | Rule-based (PE, growth, margin, D/E) | 0.0 – 1.0 |
| `confidence` (final) | Agent-synthesised combination | 0.0 – 1.0 |

---

## Notes

- **Alpha Vantage free tier** is limited to 25 requests/day and 5 requests/minute. Heavy testing may hit rate limits.
- Each call to `/analyse/agent/{ticker}` makes **multiple Claude API calls** (one inside `news_sentiment_tool` + the agent's own ReAct loop). Costs scale accordingly.
- To use stubbed price data during development, set `STUB = True` in `services/fetch_signals_alpha.py`.
