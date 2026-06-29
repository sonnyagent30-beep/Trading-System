#!/usr/bin/env python3
"""
Run Suite
=======
Runs full backtest suite.
Usage: python3 run_suite.py
"""
import subprocess, sys, os, json, logging
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/root/workspace/forex")
REPORTS_DIR = WORKSPACE / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("run_suite")

STRATEGIES = ["sma_cross", "ema_cross", "rsi_reversion"]
PAIRS = ["frxEURUSD", "frxGBPUSD", "frxUSDJPY"]

def main():
    logger.info(f"=== Suite {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC ===")
    for strat in STRATEGIES:
        for pair in PAIRS:
            logger.info(f"Running: {strat} {pair}")
            subprocess.run([sys.executable, str(WORKSPACE / "backtest.py"), "--strategy", strat, "--symbol", pair])
    logger.info("Suite complete")

if __name__ == "__main__":
    main()
