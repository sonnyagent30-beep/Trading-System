#!/usr/bin/env python3
"""
Run BB Squeeze Backtest
====================
Runs Bollinger Band Squeeze backtest.
Usage: python3 run_bb_squeeze_backtest.py
"""
import subprocess, sys
from pathlib import Path

WORKSPACE = Path("/root/workspace/forex")

def main():
    print("Running BB Squeeze backtest...")
    subprocess.run([sys.executable, str(WORKSPACE / "backtest.py"), "--strategy", "bb_rsi_revert"])

if __name__ == "__main__":
    main()
