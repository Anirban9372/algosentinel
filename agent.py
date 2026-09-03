import os
import schedule
import time
from dotenv import load_dotenv
from news import fetch_headlines
from sentiment import score_sentiment
from options import get_spy_option
from risk import check_risk
from executor import place_option_order

load_dotenv()


def run_agent():
    print("\n" + "="*50)
    print("[AGENT] Cycle started")

    # Step 1: News
    headlines = fetch_headlines()
    if not headlines:
        print("[NEWS] No headlines. Skipping.")
        return
    print(f"[NEWS] {len(headlines)} headlines fetched")
    for h in headlines[:3]:
        print(f"  → {h}")

    # Step 2: Sentiment
    try:
        signal, confidence, reason = score_sentiment(headlines)
    except Exception as e:
        print(f"[SENTIMENT] Error: {e}")
        return
    print(f"[SENTIMENT] {signal} | Confidence: {confidence:.2f} | {reason}")

    if signal == "NEUTRAL" or confidence < 0.65:
        print("[AGENT] Weak signal. No trade.")
        return

    # Step 3: Risk
    ok, msg, max_spend = check_risk()
    if not ok:
        print(f"[RISK] Blocked — {msg}")
        return
    print(f"[RISK] Approved. Max spend: ${max_spend:.2f}")

    # Step 4: Options
    contract = get_spy_option(signal)
    if not contract:
        print("[OPTIONS] No contract found. Skipping.")
        return
    print(f"[OPTIONS] Contract: {contract.symbol}")

    # Step 5: Trade
    try:
        place_option_order(contract.symbol, qty=1)
    except Exception as e:
        print(f"[EXECUTOR] Order failed: {e}")


if __name__ == "__main__":
    print("[ALGOSENTINEL] Agent starting...")
    run_agent()
    schedule.every(15).minutes.do(run_agent)
    while True:
        schedule.run_pending()
        time.sleep(1)
