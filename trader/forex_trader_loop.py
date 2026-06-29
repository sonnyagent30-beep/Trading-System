#!/usr/bin/env python3
"""
Forex Trader Loop
=================
Main trading loop.
Usage: python3 forex_trader_loop.py
"""
import time, json, logging
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("forex_trader")

BASE_DIR = Path("/root/workspace/forex")
STATE_FILE = BASE_DIR / "trader" / "state.json"
CYCLE_SECS = 30

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"cycle": 0, "positions": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def cycle():
    logger.info(f"Cycle {datetime.now(timezone.utc)}")
    state = load_state()
    state["cycle"] += 1
    save_state(state)

def main():
    logger.info("Forex Trader starting")
    while True:
        cycle()
        time.sleep(CYCLE_SECS)

if __name__ == "__main__":
    main()
