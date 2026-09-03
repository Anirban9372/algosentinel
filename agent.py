import os
import math
import schedule
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from news import fetch_headlines
from sentiment import score_sentiment
from options import get_spy_option
from risk import check_risk
from executor import place_option_order

load_dotenv()

# US Eastern timezone for market hours check
ET = ZoneInfo("America/New_York")

# Options contracts represent 100 shares each
CONTRACT_MULTIPLIER = 100


def log(tag: str, msg: str):
    """Print a timestamped, tagged log line."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{tag}] {msg}")


def is_market_open() -> bool:
    """Check if the US options market is currently open (9:30 AM – 4:00 PM ET, Mon-Fri)."""
    now_et = datetime.now(ET)
    if now_et.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    market_open = now_et.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now_et <= market_close


def run_agent():
    print("\n" + "=" * 50)
    log("AGENT", "Cycle started")

    # Pre-check: market hours
    if not is_market_open():
        now_et = datetime.now(ET)
        log("AGENT", f"Market closed (ET: {now_et.strftime('%A %I:%M %p')}). Skipping.")
        return

    # Step 1: News
    headlines = fetch_headlines()
    if not headlines:
        log("NEWS", "No headlines. Skipping.")
        return
    log("NEWS", f"{len(headlines)} headlines fetched")
    for h in headlines[:3]:
        print(f"  → {h}")

    # Step 2: Sentiment
    try:
        signal, confidence, reason = score_sentiment(headlines)
    except Exception as e:
        log("SENTIMENT", f"Error: {e}")
        return
    log("SENTIMENT", f"{signal} | Confidence: {confidence:.2f} | {reason}")

    if signal == "NEUTRAL" or confidence < 0.60:
        log("AGENT", "Weak signal. No trade.")
        return

    # Step 3: Risk
    ok, msg, max_spend = check_risk()
    if not ok:
        log("RISK", f"Blocked — {msg}")
        return
    log("RISK", f"Approved. Max spend: ${max_spend:.2f}")

    # Step 4: Options
    contract, ask_price = get_spy_option(signal)
    if not contract:
        log("OPTIONS", "No contract found. Skipping.")
        return
    log("OPTIONS", f"Contract: {contract.symbol} | Ask: ${ask_price:.2f}")

    # Step 5: Calculate quantity from max_spend
    if ask_price > 0:
        cost_per_contract = ask_price * CONTRACT_MULTIPLIER
        qty = max(1, math.floor(max_spend / cost_per_contract))
    else:
        qty = 1
    log("TRADE", f"Placing order: {qty}x {contract.symbol}")

    # Step 6: Execute
    try:
        result = place_option_order(contract.symbol, qty=qty)
        log("TRADE", f"✅ Order filled — ID: {result.id} | Status: {result.status}")
    except Exception as e:
        log("EXECUTOR", f"Order failed: {e}")


if __name__ == "__main__":
    log("ALGOSENTINEL", "Agent starting...")
    run_agent()
    schedule.every(15).minutes.do(run_agent)
    while True:
        schedule.run_pending()
        time.sleep(1)
