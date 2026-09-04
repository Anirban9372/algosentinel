# AlgoSentinel — Project Context

## What This Is
An autonomous news-sentiment-driven options trading agent built for the 
Alpaca AI Trading Agents Hackathon (lablab.ai). Deadline: Sep 4, 8:30 PM IST.

## Strategy
1. Fetch financial headlines from Google News RSS (SPY-focused)
2. Score sentiment via Gemini 3.6 Flash → BULLISH / BEARISH / NEUTRAL
3. If directional signal with confidence ≥ 0.60 → find SPY options contract
4. Risk gate checks equity floor ($85k) and max positions (3)
5. Calculate order quantity from max spend budget and contract ask price
6. Place market order via Alpaca paper trading API
7. Loop every 15 minutes via `schedule` (only during market hours)

## File Structure

algosentinel/
├── .env              # API keys (never commit)
├── .gitignore        # Excludes .env, venv/, __pycache__/
├── requirements.txt  # Pinned dependencies
├── README.md         # Project overview + hackathon write-up
├── context.md        # This file — internal project context
├── agent.py          # Main loop — entry point, CLI account check at startup
├── news.py           # Google News RSS headline fetcher
├── sentiment.py      # Gemini LLM sentiment scorer
├── options.py        # SPY options chain selector (ATM-sorted, live ask price)
├── risk.py           # Risk gate (equity floor, max positions)
├── executor.py       # Alpaca order placement


## Environment Variables (.env)

ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
GEMINI_API_KEY=...


## Stack
- Python 3.14.4
- alpaca-py 0.44.0 (paper trading, options)
- google-genai 2.22.0 (Gemini 3.6 Flash)
- schedule, requests, python-dotenv

## Alpaca Config
- Paper trading only (paper=True in all clients)
- Target asset: SPY options
- Contract type: CALL if BULLISH, PUT if BEARISH
- Expiry window: today + 7 days
- Order type: Market, DAY
- Starting balance: $100,000
- CLI integration: `alpaca account get` called at startup for account status

## Risk Gates
- Max 5% equity per trade ($5,000 on $100k)
- Max 3 open positions simultaneously
- Hard floor: halt if equity < $85,000
- No trade on NEUTRAL signal
- No trade if confidence < 0.60
- No trade outside US market hours (9:30 AM – 4:00 PM ET)

## Current Status
- All modules written and tested
- Agent runs and fetches live headlines (Google News RSS)
- Sentiment scoring works via Gemini 3.6 Flash (google-genai SDK)
- Paper account live at Alpaca
- Market hours check prevents wasted cycles outside trading window
- Contract quantity calculated from risk-gated budget
- CLI integration added — `alpaca account get` runs at startup for hackathon compliance
- Options module uses live stock data API for real SPY price + live option quotes
- US market opens 7:00 PM IST — agent must make trades before 8:30 PM IST deadline

## Known Issues / Warnings
- Gemini AFC warning on generate_content — cosmetic only, does not affect output
- Options chain may return empty outside market hours — handled by market hours check
- CLI `alpaca` command must be installed and on PATH for cli_account_check()

## What Needs To Happen Next
1. Start agent at ~6:50 PM IST
2. Monitor logs for BULLISH/BEARISH signal after 7:00 PM IST market open
3. Confirm at least 1 paper trade executes before 8:30 PM IST
4. Record screen of agent placing trade for video demo
5. Submit on lablab.ai with paper account ID

## Hackathon Requirements Checklist
- [x] Autonomous AI trading agent
- [x] Alpaca Trading API used
- [x] CLI used (alpaca CLI account check at startup)
- [x] Options trading incorporated
- [x] Paper trading environment
- [x] Fresh paper account ($100k starting balance)
- [ ] Video demo
- [x] One-page write-up (README.md)
- [ ] Submit on lablab.ai with paper account ID

## Team
- Team name: AlgoSentinel
- Platform: lablab.ai Alpaca AI Trading Agents Hackathon