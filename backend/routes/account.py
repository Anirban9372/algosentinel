from fastapi import APIRouter, HTTPException
from alpaca.trading.client import TradingClient
import os

router = APIRouter(prefix="/api/account", tags=["account"])


def get_client():
    return TradingClient(
        api_key=os.getenv("ALPACA_API_KEY"),
        secret_key=os.getenv("ALPACA_SECRET_KEY"),
        paper=True
    )


@router.get("/")
def get_account():
    try:
        client = get_client()
        account = client.get_account()
        positions = client.get_all_positions()
        return {
            "account_number": account.account_number,
            "equity": float(account.equity),
            "cash": float(account.cash),
            "buying_power": float(account.buying_power),
            "portfolio_value": float(account.portfolio_value),
            "positions_count": len(positions)
        }
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Alpaca API error: {str(e)}")


@router.get("/positions")
def get_positions():
    try:
        client = get_client()
        positions = client.get_all_positions()

        return [
            {
                "symbol": p.symbol,
                "qty": int(p.qty),
                "avg_fill_price": float(p.avg_fill_price),
                "market_value": float(p.market_value),
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_plpc": float(p.unrealized_plpc)
            }
            for p in positions
        ]
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Alpaca API error: {str(e)}")
