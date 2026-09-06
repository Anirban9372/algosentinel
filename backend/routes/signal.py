from fastapi import APIRouter
import json
import os
from datetime import datetime

router = APIRouter(prefix="/api/signal", tags=["signal"])

SIGNAL_LOG = "signals.log"


@router.get("/latest")
def get_latest_signal():
    """Return latest sentiment signal."""
    try:
        if os.path.exists(SIGNAL_LOG):
            with open(SIGNAL_LOG, "r") as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    return json.loads(lines[-1])
    except Exception:
        pass

    return {
        "signal": "NEUTRAL",
        "confidence": 0.0,
        "reason": "No signals yet",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/history")
def get_signal_history(limit: int = 20):
    """Return last N signals."""
    signals = []
    try:
        if os.path.exists(SIGNAL_LOG):
            with open(SIGNAL_LOG, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            signals.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
    except Exception:
        pass
    return signals[-limit:]
