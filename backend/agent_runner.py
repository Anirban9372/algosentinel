import asyncio
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from agent import run_agent as sync_run_agent

executor = ThreadPoolExecutor(max_workers=1)


def log_signal(signal: str, confidence: float, reason: str):
    entry = {
        "signal": signal,
        "confidence": confidence,
        "reason": reason,
        "timestamp": datetime.now().isoformat()
    }
    with open("signals.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def log_trade(symbol: str, qty: int, status: str, order_id: str = None, pnl: float = 0):
    entry = {
        "symbol": symbol,
        "qty": qty,
        "status": status,
        "order_id": order_id,
        "pnl": pnl,
        "timestamp": datetime.now().isoformat()
    }
    with open("trades.log", "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


async def run_agent_async(broadcast_fn):
    """Runs the blocking agent code in a thread pool so it doesn't freeze the API."""
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(executor, sync_run_agent)
        if result:
            await broadcast_fn({"type": "cycle_complete", "data": result})
    except Exception as e:
        await broadcast_fn({"type": "error", "message": str(e)})
