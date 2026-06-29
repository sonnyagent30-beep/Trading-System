#!/usr/bin/env python3
"""
London Breakout Loop
====================
London session breakout strategy.
Usage: python3 london_breakout_loop.py
"""
import time, json, logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("london_breakout")

BASE_DIR = Path("/root/workspace/forex")
STATE_FILE = BASE_DIR / "trader" / "state.json"
CYCLE_SECS = 60

# London session: 08:00-11:00 WAT
LONDON_START = 8
LONDON_END = 11

def is_london_session():
    hour = datetime.now(timezone.utc).hour + 1
    return LONDON_START <= hour < LONDON_END

def main():
    logger.info("London Breakout starting")
    while True:
        if is_london_session():
            logger.info("London session active")
        time.sleep(CYCLE_SECS)

if __name__ == "__main__":
    main()
