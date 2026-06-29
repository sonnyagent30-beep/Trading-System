#!/usr/bin/env python3
"""
Run Master BT
=========
Master backtest runner.
Usage: python3 run_master_bt.py
"""
import subprocess, sys
from pathlib import Path

WORKSPACE = Path("/root/workspace/forex")

PAIRS = ["frxEURUSD", "frxGBPUSD", "frxUSDJPY", "frxAUDUSD", "frxXAUUSD"]

def main():
    for pair in PAIRS:
        print(f"Backtesting {pair}...")
        subprocess.run([sys.executable, str(WORKSPACE / "backtest.py"), "--symbol", pair])

if __name__ == "__main__":
    main()
