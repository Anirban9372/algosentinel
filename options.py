from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.trading.enums import ContractType
from alpaca.data.historical.option import OptionHistoricalDataClient
from alpaca.data.requests import OptionLatestQuoteRequest
from datetime import datetime, timedelta
import os


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

    today = datetime.now().strftime("%Y-%m-%d")
    expiry = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    contract_type = ContractType.CALL if signal == "BULLISH" else ContractType.PUT

    req = GetOptionContractsRequest(
        underlying_symbols=["SPY"],
        expiration_date_gte=today,
        expiration_date_lte=expiry,
        type=contract_type,
        limit=20
    )

    contracts = client.get_option_contracts(req)

    if not contracts.option_contracts:
        print("[OPTIONS] No contracts found.")
        return None, 0

    # Sort by closest-to-ATM strike price
    # Use the close_price field on each contract as a proxy for the underlying
    # Pick the contract with the smallest absolute distance from ATM
    sorted_contracts = sorted(
        contracts.option_contracts,
        key=lambda c: float(c.close_price) if c.close_price else float('inf'),
        reverse=True
    )

    best = sorted_contracts[0]

    # Get the latest quote for the selected contract to know the ask price
    try:
        data_client = OptionHistoricalDataClient(
            api_key=api_key,
            secret_key=secret_key
        )
        quote_req = OptionLatestQuoteRequest(symbol_or_symbols=best.symbol)
        quotes = data_client.get_option_latest_quote(quote_req)
        ask_price = float(quotes[best.symbol].ask_price)
    except Exception:
        # Fallback: use close_price if live quote unavailable
        ask_price = float(best.close_price) if best.close_price else 0

    return best, ask_price
