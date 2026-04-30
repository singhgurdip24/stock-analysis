import os
import json
import anthropic
from dotenv import load_dotenv
from models.stockModels import StockSignals

load_dotenv()

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))

def analyse_with_claude(signals: StockSignals) -> dict:
    data = json.dumps(signals.model_dump(), indent=2)

    prompt = f"""Here is stock analysis data for a stock:

{data}

Analyse this data and respond in the following format exactly:

📈 STOCK ANALYSIS REPORT
========================

🔵 SHORT TERM OUTLOOK (1-2 weeks)
<your short term outlook here>

🟡 MEDIUM TERM OUTLOOK (1-3 months)
<your medium term outlook here>

🟢 LONG TERM OUTLOOK (6-12 months)
<your long term outlook here>

🧠 REASONING
<explain your reasoning based on the MA20, MA50, RSI, trend, and RSI signal values>

Keep each section concise — 2 to 3 sentences maximum."""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return {"analysis": response.content[0].text}
