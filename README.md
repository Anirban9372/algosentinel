# AlgoSentinel 🛡️

> **Autonomous AI-powered options trading agent** that reads live market sentiment from news headlines and executes SPY options trades — fully hands-off.

Built for the [Alpaca AI Trading Agents Hackathon](https://lablab.ai) by **Team AlgoSentinel**.

---

## 🎯 What It Does

AlgoSentinel is a **fully autonomous trading agent** that:

1. **Reads** live financial headlines from Google News RSS
2. **Thinks** using Google Gemini 3.6 Flash to score market sentiment
3. **Decides** whether the signal is strong enough to trade (≥ 60% confidence)
4. **Checks** risk gates before every trade (equity floor, position limits)
5. **Trades** SPY options via the Alpaca paper trading API
6. **Loops** every 15 minutes — no human intervention needed

```
┌─────────────┐     ┌──────────────────┐     ┌───────────┐     ┌──────────────┐     ┌───────────────┐
│ Google News  │────▶│  Gemini 3.6 Flash │────▶│ Risk Gate │────▶│ Options Pick │────▶│ Alpaca Trade  │
│  RSS Feed    │     │  Sentiment AI     │     │ (5 checks)│     │ (ATM SPY)    │     │ (Paper Acct)  │
└─────────────┘     └──────────────────┘     └───────────┘     └──────────────┘     └───────────────┘
```

---

## 🧠 AI-Powered Decision Making

The core intelligence is powered by **Google Gemini 3.6 Flash**:

- Receives 10 live financial headlines about SPY / S&P 500
- Analyzes aggregate market sentiment in real-time
- Returns a structured JSON decision:
  ```json
  {
    "signal": "BULLISH",
    "confidence": 0.78,
    "reason": "Strong rally signals across tech and financials"
  }
  ```
- The AI **is** the decision-maker — it drives the entire trade-or-no-trade logic
- Only acts on **directional signals** (BULLISH/BEARISH) with confidence ≥ 0.60

---

## 🏗️ Architecture

| Module | Purpose |
|---|---|
| [`agent.py`](agent.py) | Main loop — orchestrates the full pipeline every 15 min |
| [`news.py`](news.py) | Fetches live headlines from Google News RSS |
| [`sentiment.py`](sentiment.py) | Gemini 3.6 Flash sentiment scoring → BULLISH/BEARISH/NEUTRAL |
| [`options.py`](options.py) | Finds best SPY option contract (ATM-sorted, live quotes) |
| [`risk.py`](risk.py) | Risk gate — equity floor, max positions, per-trade budget |
| [`executor.py`](executor.py) | Submits market orders via Alpaca Trading API |

```
algosentinel/
├── agent.py          # Entry point — main trading loop
├── news.py           # Google News RSS headline fetcher
├── sentiment.py      # Gemini LLM sentiment scorer
├── options.py        # SPY options chain selector
├── risk.py           # Risk gate (equity floor, max positions)
├── executor.py       # Alpaca order placement
├── requirements.txt  # Pinned Python dependencies
├── .env              # API keys (not committed)
└── .gitignore
```

---

## 🛡️ Risk Management

Every trade passes through **5 risk gates** before execution:

| Gate | Rule | Threshold |
|---|---|---|
| 💰 Equity Floor | Halt trading if account balance drops too low | > $85,000 |
| 📊 Position Limit | Cap simultaneous open positions | ≤ 3 |
| 💵 Per-Trade Cap | Limit exposure on any single trade | ≤ 5% of equity |
| 📡 Signal Filter | Only trade on directional sentiment | BULLISH or BEARISH |
| 🎯 Confidence Filter | Require high-confidence signals | ≥ 0.60 |
| 🕐 Market Hours | Only trade when US options market is open | 9:30 AM – 4:00 PM ET |

---

## 📈 Trading Strategy

- **Asset**: SPY options (S&P 500 ETF)
- **Contract Selection**: CALL if BULLISH, PUT if BEARISH
- **Strike Selection**: Closest to ATM (at-the-money), within ±3% of current SPY price
- **Expiry Window**: Today + 7 days
- **Order Type**: Market order, DAY time-in-force
- **Quantity**: Calculated from risk-gated budget ÷ contract cost (100x multiplier)
- **Pricing**: Live ask quotes from Alpaca Options Data API

---

## 🔧 Alpaca Integration

- **Paper Trading**: All API calls use `paper=True` — no real money
- **Trading API**: Account info, positions, options contract lookup, order submission
- **Options Data API**: Live option quotes for accurate contract pricing
- **Stock Data API**: Real-time SPY price for ATM strike selection
- **Starting Balance**: $100,000 paper account

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/Anirban9372/algosentinel.git
cd algosentinel

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your keys (see below)

# Run the agent
python3 agent.py
```

### Environment Variables

Create a `.env` file with:

```env
ALPACA_API_KEY=your_alpaca_paper_api_key
ALPACA_SECRET_KEY=your_alpaca_paper_secret_key
GEMINI_API_KEY=your_google_gemini_api_key
```

- **Alpaca Keys**: Get from [app.alpaca.markets](https://app.alpaca.markets) → Paper Trading → API Keys
- **Gemini Key**: Get from [aistudio.google.com](https://aistudio.google.com/apikey)

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.14 | Runtime |
| [`alpaca-py`](https://pypi.org/project/alpaca-py/) 0.44.0 | Trading API, options data, account management |
| [`google-genai`](https://pypi.org/project/google-genai/) 2.22.0 | Gemini 3.6 Flash for sentiment analysis |
| `schedule` | 15-minute autonomous trading loop |
| `requests` | RSS feed fetching |
| `python-dotenv` | Secure environment variable management |

---

## 📋 How It Works (Detailed Flow)

```
Every 15 minutes:
│
├── 1. Market Hours Check
│   └── Is it 9:30 AM – 4:00 PM ET, Mon-Fri?
│       ├── No  → Skip cycle, wait 15 min
│       └── Yes → Continue ↓
│
├── 2. Fetch Headlines
│   └── Google News RSS → 10 latest SPY/S&P 500 headlines
│
├── 3. AI Sentiment Analysis
│   └── Gemini 3.6 Flash → {signal, confidence, reason}
│       ├── NEUTRAL or confidence < 0.60 → Skip, no trade
│       └── BULLISH/BEARISH with confidence ≥ 0.60 → Continue ↓
│
├── 4. Risk Gate
│   ├── Equity > $85k?
│   ├── Open positions < 3?
│   └── Calculate max spend (5% of equity)
│       ├── Any check fails → Block trade
│       └── All pass → Continue ↓
│
├── 5. Options Selection
│   ├── Get live SPY price
│   ├── Find ATM options (±3% strike range, 7-day expiry)
│   ├── Sort by closest to ATM
│   └── Get live ask price for best contract
│
└── 6. Execute Trade
    ├── Calculate quantity from budget
    └── Submit market order via Alpaca
```

---

## 👥 Team

- **Team Name**: AlgoSentinel
- **Hackathon**: [Alpaca AI Trading Agents Hackathon](https://lablab.ai) (lablab.ai)

---

## ⚠️ Disclaimer

This project is built for a hackathon and uses **paper trading only**. It is not financial advice and should not be used with real money without extensive testing, backtesting, and risk assessment.