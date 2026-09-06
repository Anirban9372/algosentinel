from fastapi import APIRouter
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/trades", tags=["trades"])

TRADES_LOG = "trades.log"


@router.get("/")
def get_trades(limit: int = 50):
    """Return last N trades from log."""
    trades = []
    try:
        if os.path.exists(TRADES_LOG):
            with open(TRADES_LOG, "r") as f:
                for line in f:
                    try:
                        # Attempt to parse json
                        parsed = json.loads(line)
                        trades.append(parsed)
                    except json.JSONDecodeError:
                        # Fallback for old logs that aren't JSON
                        trades.append({"message": line.strip()})
    except Exception:
        pass
    return trades[-limit:]


@router.get("/stats")
def get_trade_stats():
    """P&L summary, win rate, etc."""
    trades = []
    try:
        if os.path.exists(TRADES_LOG):
            with open(TRADES_LOG, "r") as f:
                for line in f:
                    try:
                        parsed = json.loads(line)
                        if "status" in parsed:
                            trades.append(parsed)
                    except json.JSONDecodeError:
                        pass
    except Exception:
        pass

    filled = [t for t in trades if t.get(
        "status") in ["filled", "accepted", "OrderStatus.PENDING_NEW"]]

    return {
        "total_trades": len(filled),
        "avg_p_l": sum(t.get("pnl", 0) for t in filled) / len(filled) if filled else 0,
        "win_rate": len([t for t in filled if t.get("pnl", 0) > 0]) / len(filled) if filled else 0
    }
