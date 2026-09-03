from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOptionContractsRequest
from alpaca.trading.enums import ContractType
from datetime import datetime, timedelta
import os


def get_spy_option(signal: str):
    client = TradingClient(
        api_key=os.getenv("ALPACA_API_KEY"),
        secret_key=os.getenv("ALPACA_SECRET_KEY"),
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
        limit=5
    )

    contracts = client.get_option_contracts(req)

    if not contracts.option_contracts:
        print("[OPTIONS] No contracts found.")
        return None

    return contracts.option_contracts[0]
