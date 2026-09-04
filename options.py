from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.trading.enums import ContractType
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest, OptionLatestQuoteRequest
from datetime import datetime, timedelta
import os


def _get_spy_price(api_key: str, secret_key: str) -> float:
    """Get the current SPY price from Alpaca stock data API."""
    client = StockHistoricalDataClient(
        api_key=api_key,
        secret_key=secret_key
    )
    req = StockLatestTradeRequest(symbol_or_symbols="SPY")
    trades = client.get_stock_latest_trade(req)
    return float(trades["SPY"].price)


def get_spy_option(signal: str):
    """Find the best SPY option contract for the given signal.

    Returns (contract, ask_price) or (None, 0) if nothing found.
    Picks the contract with a strike closest to ATM (current SPY price).
    """
    api_key = os.getenv("ALPACA_API_KEY")
    secret_key = os.getenv("ALPACA_SECRET_KEY")

    client = TradingClient(
        api_key=api_key,
        secret_key=secret_key,
        paper=True
    )

    # Get actual SPY price from stock data API
    try:
        spy_price = _get_spy_price(api_key, secret_key)
    except Exception as e:
        print(f"[OPTIONS] Could not get SPY price: {e}")
        return None, 0
    print(f"[OPTIONS] SPY price: ${spy_price:.2f}")

    today = datetime.now().strftime("%Y-%m-%d")
    expiry = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    contract_type = ContractType.CALL if signal == "BULLISH" else ContractType.PUT

    # Filter contracts with strikes near ATM (±3% of SPY price)
    margin = spy_price * 0.03
    strike_lo = str(round(spy_price - margin, 2))
    strike_hi = str(round(spy_price + margin, 2))

    req = GetOptionContractsRequest(
        underlying_symbols=["SPY"],
        expiration_date_gte=today,
        expiration_date_lte=expiry,
        type=contract_type,
        strike_price_gte=strike_lo,
        strike_price_lte=strike_hi,
        limit=20
    )

    contracts = client.get_option_contracts(req)

    if not contracts.option_contracts:
        print(
            f"[OPTIONS] No ATM contracts found (strikes ${strike_lo}–${strike_hi}).")
        return None, 0

    # Sort by closest to ATM
    sorted_contracts = sorted(
        contracts.option_contracts,
        key=lambda c: abs(c.strike_price - spy_price)
    )

    best = sorted_contracts[0]
    print(
        f"[OPTIONS] Selected: {best.name} | Strike: ${best.strike_price:.2f}")

    # Get live ask price for accurate cost calculation
    try:
        data_client = OptionHistoricalDataClient(
            api_key=api_key,
            secret_key=secret_key
        )
        quote_req = OptionLatestQuoteRequest(symbol_or_symbols=best.symbol)
        quotes = data_client.get_option_latest_quote(quote_req)
        ask_price = float(quotes[best.symbol].ask_price)
    except Exception:
        # Fallback: rough estimate using intrinsic value + $2 time premium
        intrinsic = max(0, spy_price - best.strike_price) if contract_type == ContractType.CALL \
            else max(0, best.strike_price - spy_price)
        ask_price = intrinsic + 2.0

    return best, ask_price
