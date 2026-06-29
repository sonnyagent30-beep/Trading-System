#!/usr/bin/env python3
"""
Run Daily Cycle
=============
Wrapper — runs the architect cycle, backtest, and manager.
Usage: python3 run_daily.py
"""
import subprocess, sys, os, logging
from pathlib import Path
from datetime import datetime, timezone, timedelta

WORKSPACE = Path("/root/workspace/forex")
LOGS_DIR = WORKSPACE / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "run_daily.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("run_daily")

def main():
    logger.info(f"=== Daily Cycle {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC ===")
    
    # Run architect cycle
    logger.info("Running architect cycle...")
    result = subprocess.run([
        sys.executable, str(WORKSPACE / "architect_cycle.py"),
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        logger.error(f"Architect cycle failed: {result.stderr}")
    else:
        logger.info(f"Architect cycle complete: {result.stdout[:500]}")
    
    logger.info("Daily cycle complete")

if __name__ == "__main__":
    main()
