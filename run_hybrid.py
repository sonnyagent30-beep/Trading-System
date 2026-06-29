#!/usr/bin/env python3
"""
Run Hybrid
==========
Runs hybrid backtest.
Usage: python3 run_hybrid.py
"""
import subprocess, sys
from pathlib import Path

WORKSPACE = Path("/root/workspace/forex")

def main():
    print("Running hybrid backtest...")
    subprocess.run([sys.executable, str(WORKSPACE / "backtest.py"), "--strategy", "ema_trend_4h"])

if __name__ == "__main__":
    main()
