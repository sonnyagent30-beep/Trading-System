#!/usr/bin/env python3
"""
MATH AMP Trader Loop
================
Trading loop for MATH AMP strategy.
Usage: python3 mATH_AMP_trader_loop.py
"""
import time, json, logging
from datetime import datetime, timezone
from pathlib import Path
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("math_amp_trader")

PAIRS = {"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X"}
CYCLE_SECS = 300

def check_signal(pair: str, yf_pair: str) -> bool:
    ticker = yf.Ticker(yf_pair)
    df = ticker.history(period="30d", interval="4h")
    if len(df) < 20:
        return False
    close = df["Close"]
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    return close.iloc[-1] > ema20.iloc[-1] and ema20.iloc[-1] > ema50.iloc[-1]

def main():
    logger.info("MATH AMP Trader starting")
    while True:
        for pair, yf_pair in PAIRS.items():
            if check_signal(pair, yf_pair):
                logger.info(f"BUY SIGNAL: {pair}")
        time.sleep(CYCLE_SECS)

if __name__ == "__main__":
    main()
