# AlgoSentinel 🛡️

> Autonomous AI-powered options trading agent that reads market sentiment from live news and executes SPY options trades via the Alpaca paper trading API.

Built for the [Alpaca AI Trading Agents Hackathon](https://lablab.ai) by **Team AlgoSentinel**.

---

## How It Works

```
News Headlines ──→ Gemini AI Sentiment ──→ Risk Gate ──→ Options Picker ──→ Trade Execution
   (Google News)     (gemini-3.6-flash)    (equity/     (closest ATM      (Alpaca Paper
                                            positions)   SPY option)        Trading API)
```

### Pipeline (every 15 minutes)

1. **Fetch Headlines** — Pulls latest SPY & S&P 500 headlines from Google News RSS
2. **Score Sentiment** — Gemini 3.6 Flash analyzes headlines → returns `BULLISH`, `BEARISH`, or `NEUTRAL` with a confidence score
3. **Risk Check** — Verifies equity > $85k, < 3 open positions, and calculates max 5% per-trade spend
4. **Select Option** — Finds the best SPY option contract (CALL for bullish, PUT for bearish) expiring within 7 days, sorted by premium
5. **Execute Trade** — Places a market order via Alpaca's paper trading API, with quantity calculated from the risk-gated budget

The agent only trades on directional signals (BULLISH/BEARISH) with confidence ≥ 0.60.

---

## Architecture

| Module | Purpose |
|---|---|
| `agent.py` | Main loop — orchestrates the pipeline, market hours check, logging |
| `news.py` | RSS headline fetcher (Google News) |
| `sentiment.py` | Gemini LLM sentiment scoring |
| `options.py` | SPY options chain lookup + ATM sorting |
| `risk.py` | Risk gate — equity floor, max positions, per-trade budget |
| `executor.py` | Alpaca order submission |

---

## Risk Management

| Gate | Threshold |
|---|---|
| Minimum equity | $85,000 |
| Max open positions | 3 |
| Max per-trade spend | 5% of equity |
| Signal filter | Skip NEUTRAL signals |
| Confidence filter | Skip if confidence < 0.60 |
| Market hours | Only trade 9:30 AM – 4:00 PM ET |

---

## AI Integration

- **Model**: Google Gemini 3.6 Flash via `google-genai` SDK
- **Task**: Financial sentiment analysis on live news headlines
- **Output**: Structured JSON with `signal`, `confidence`, and `reason`
- **Role**: The AI is the decision-maker — it determines whether the market outlook is bullish, bearish, or neutral, driving the entire trade-or-no-trade logic

---

## Alpaca Infrastructure

- Paper trading environment (`paper=True`)
- Trading API: account info, positions, options contracts, order submission
- Options Data API: live quotes for accurate contract pricing
- Starting balance: $100,000
- Target asset: SPY options (CALL/PUT)

---

## Quick Start

```bash
# Clone
git clone https://github.com/Anirban9372/algosentinel.git
cd algosentinel

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your Alpaca and Gemini API keys

# Run
python agent.py
```

### Environment Variables

```
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
GEMINI_API_KEY=your_gemini_key
```

---

## Stack

- Python 3.14
- `alpaca-py` — Trading & options data API
- `google-genai` — Gemini 3.6 Flash sentiment analysis
- `schedule` — 15-minute trading loop
- `requests` — RSS feed fetching
- `python-dotenv` — Environment variable management
