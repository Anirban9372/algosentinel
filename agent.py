import subprocess
import os
import math
import schedule
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
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

# Exit thresholds
STOP_LOSS_PCT   = -0.50   # exit at 50% loss
TAKE_PROFIT_PCT =  1.00   # exit at 100% gain

# Persistent log file
TRADE_LOG = "trades.log"


# ── Helpers ──────────────────────────────────────────────────────────────────

def log(tag: str, msg: str):
    """Print a timestamped, tagged log line."""
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{tag}] {msg}")


def log_trade(msg: str):
    """Append a timestamped entry to trades.log."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    with open(TRADE_LOG, "a") as f:
        f.write(line)
    log("LOG", msg)


def is_market_open() -> bool:
    """Check if the US options market is currently open (9:30 AM – 4:00 PM ET, Mon-Fri)."""
    now_et = datetime.now(ET)
    if now_et.weekday() >= 5:  # Saturday=5, Sunday=6
        return False
    market_open  = now_et.replace(hour=9,  minute=30, second=0, microsecond=0)
    market_close = now_et.replace(hour=16, minute=0,  second=0, microsecond=0)
    return market_open <= now_et <= market_close


def get_trading_client() -> TradingClient:
    return TradingClient(
        api_key=os.getenv("ALPACA_API_KEY"),
        secret_key=os.getenv("ALPACA_SECRET_KEY"),
        paper=True
    )


def cli_account_check():
    result = subprocess.run(
        ["alpaca", "account", "get"],
        capture_output=True, text=True,
        env={**os.environ,
             "ALPACA_API_KEY": os.getenv("ALPACA_API_KEY"),
             "ALPACA_SECRET_KEY": os.getenv("ALPACA_SECRET_KEY")}
    )
    if result.returncode == 0:
        log("CLI", f"Account OK — {result.stdout[:100].strip()}")
    else:
        log("CLI", f"Warning: {result.stderr[:100].strip()}")


# ── Priority 3: Duplicate prevention ─────────────────────────────────────────

def get_spy_option_positions(client: TradingClient) -> list:
    """Return all open positions whose symbol starts with 'SPY' (options)."""
    try:
        positions = client.get_all_positions()
        return [p for p in positions if p.symbol.startswith("SPY")]
    except Exception as e:
        log("RISK", f"Could not fetch positions: {e}")
        return []


# ── Priority 1: Auto-exit monitor ────────────────────────────────────────────

def monitor_exits(client: TradingClient):
    """Check every open SPY option position and exit on 50% loss or 100% gain."""
    spy_positions = get_spy_option_positions(client)
    if not spy_positions:
        return

    for pos in spy_positions:
        try:
            unrealized_pct = float(pos.unrealized_plpc)   # e.g. -0.52 = -52%
            symbol = pos.symbol
            pl_pct = unrealized_pct * 100

            if unrealized_pct <= STOP_LOSS_PCT:
                log("EXIT", f"🔴 Stop-loss hit on {symbol} ({pl_pct:.1f}%) — closing position")
                log_trade(f"EXIT STOP-LOSS | {symbol} | P&L: {pl_pct:.1f}%")
                client.close_position(symbol)

            elif unrealized_pct >= TAKE_PROFIT_PCT:
                log("EXIT", f"🟢 Take-profit hit on {symbol} ({pl_pct:.1f}%) — closing position")
                log_trade(f"EXIT TAKE-PROFIT | {symbol} | P&L: {pl_pct:.1f}%")
                client.close_position(symbol)

            else:
                log("MONITOR", f"{symbol} | P&L: {pl_pct:.1f}% — holding")

        except Exception as e:
            log("EXIT", f"Error closing {pos.symbol}: {e}")


# ── Main agent loop ───────────────────────────────────────────────────────────

def run_agent():
    print("\n" + "=" * 50)
    log("AGENT", "Cycle started")

    # Pre-check: market hours
    if not is_market_open():
        now_et = datetime.now(ET)
        log("AGENT",
            f"Market closed (ET: {now_et.strftime('%A %I:%M %p')}). Skipping.")
        return

    client = get_trading_client()

    # Priority 1: check exits before anything else
    monitor_exits(client)

    # Priority 3: skip if already holding SPY options (duplicate prevention)
    spy_positions = get_spy_option_positions(client)
    if spy_positions:
        symbols = ", ".join(p.symbol for p in spy_positions)
        log("RISK", f"Already holding SPY options: {symbols} — skipping new entry")
        log_trade(f"SKIP — already holding: {symbols}")
        return

    # Step 1: News
    headlines = fetch_headlines()
    if not headlines:
        log("NEWS", "No headlines. Skipping.")
        log_trade("SKIP — no headlines")
        return
    log("NEWS", f"{len(headlines)} headlines fetched")
    for h in headlines[:3]:
        print(f"  → {h}")

    # Step 2: Sentiment
    try:
        signal, confidence, reason = score_sentiment(headlines)
    except Exception as e:
        log("SENTIMENT", f"Error: {e}")
        log_trade(f"SKIP — sentiment error: {e}")
        return
    log("SENTIMENT", f"{signal} | Confidence: {confidence:.2f} | {reason}")

    if signal == "NEUTRAL" or confidence < 0.60:
        log("AGENT", "Weak signal. No trade.")
        log_trade(f"SKIP — {signal} | confidence {confidence:.2f} | {reason}")
        return

    # Step 3: Risk
    ok, msg, max_spend = check_risk()
    if not ok:
        log("RISK", f"Blocked — {msg}")
        log_trade(f"SKIP — risk gate: {msg}")
        return
    log("RISK", f"Approved. Max spend: ${max_spend:.2f}")

    # Step 4: Options
    contract, ask_price = get_spy_option(signal)
    if not contract:
        log("OPTIONS", "No contract found. Skipping.")
        log_trade(f"SKIP — no options contract found for {signal}")
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
        log("TRADE",
            f"✅ Order filled — ID: {result.id} | Status: {result.status}")
        log_trade(
            f"BUY | {contract.symbol} | qty={qty} | ask=${ask_price:.2f} "
            f"| signal={signal} | conf={confidence:.2f} | {reason}"
        )
    except Exception as e:
        log("EXECUTOR", f"Order failed: {e}")
        log_trade(f"ERROR — order failed for {contract.symbol}: {e}")


if __name__ == "__main__":
    log("ALGOSENTINEL", "Agent starting...")
    cli_account_check()
    run_agent()
    schedule.every(15).minutes.do(run_agent)
    while True:
        schedule.run_pending()
        time.sleep(1)
