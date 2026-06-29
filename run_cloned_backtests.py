#!/usr/bin/env python3
"""
Run Cloned Backtests
=================
Runs cloned backtests.
Usage: python3 run_cloned_backtests.py
"""
import subprocess, sys
from pathlib import Path

WORKSPACE = Path("/root/workspace/forex")

def main():
    print("Running cloned backtests...")
    for strat in ["ema_cross", "sma_cross"]:
        subprocess.run([sys.executable, str(WORKSPACE / "backtest.py"), "--strategy", strat])

if __name__ == "__main__":
    main()
