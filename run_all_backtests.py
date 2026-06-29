#!/usr/bin/env python3
"""
Run All Backtests
===============
Runs multiple backtests in sequence.
Usage: python3 run_all_backtests.py
"""
import subprocess, sys, os, json, logging
from pathlib import Path
from datetime import datetime, timezone

WORKSPACE = Path("/root/workspace/forex")
REPORTS_DIR = WORKSPACE / "reports"
LOGS_DIR = WORKSPACE / "logs"
REPORTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "run_all_backtests.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("run_all_backtests")

STRATEGIES = ["sma_cross", "ema_cross", "rsi_reversion", "ema_trend_4h"]
PAIRS = ["frxEURUSD", "frxGBPUSD", "frxUSDJPY", "frxAUDUSD", "frxXAUUSD"]

def run_backtest(strategy: str, pair: str, days: int = 365):
    logger.info(f"Running backtest: {strategy} {pair}")
    result = subprocess.run([
        sys.executable, str(WORKSPACE / "backtest.py"),
        "--strategy", strategy,
        "--symbol", pair,
        "--days", str(days),
    ], capture_output=True, text=True)
    return result.returncode == 0

def main():
    logger.info(f"=== Backtest Suite {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC ===")
    
    results = {}
    for strat in STRATEGIES:
        results[strat] = {}
        for pair in PAIRS:
            success = run_backtest(strat, pair)
            results[strat][pair] = success
    
    with open(REPORTS_DIR / "backtest_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Backtest suite complete: {results}")

if __name__ == "__main__":
    main()
