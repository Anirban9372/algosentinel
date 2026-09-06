from alpaca.trading.client import TradingClient
import os

MAX_POSITIONS = 3
MIN_EQUITY = 85000.0
MAX_TRADE_PCT = 0.05


def check_risk():
    client = TradingClient(
        api_key=os.getenv("ALPACA_API_KEY"),
        secret_key=os.getenv("ALPACA_SECRET_KEY"),
        paper=True
    )

    account = client.get_account()
    equity = float(account.equity)

    if equity < MIN_EQUITY:
        return False, f"Equity too low: ${equity:.2f}", 0

    positions = client.get_all_positions()
    if len(positions) >= MAX_POSITIONS:
        return False, f"Max positions reached: {len(positions)}", 0

    max_spend = equity * MAX_TRADE_PCT
    return True, "OK", max_spend
