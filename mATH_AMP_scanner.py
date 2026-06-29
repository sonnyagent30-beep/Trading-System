#!/usr/bin/env python3
"""
MATH AMP Scanner
==============
Scans for MATH AMP signals.
Usage: python3 mATH_AMP_scanner.py
"""
import json, logging
from datetime import datetime, timezone
from pathlib import Path
import yfinance as yf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("math_amp_scanner")

PAIRS = {"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "XAUUSD": "GC=F"}

def check_math_amp(pair: str, yf_pair: str) -> dict:
    ticker = yf.Ticker(yf_pair)
    df = ticker.history(period="30d", interval="4h")
    if len(df) < 20:
        return {"signal": False}
    
    close = df["Close"]
    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()
    
    above_ema = close.iloc[-1] > ema20.iloc[-1]
    bullish = ema20.iloc[-1] > ema50.iloc[-1]
    
    return {
        "signal": above_ema and bullish,
        "price": close.iloc[-1],
        "ema20": ema20.iloc[-1],
        "ema50": ema50.iloc[-1],
    }

def main():
    signals = []
    for pair, yf_pair in PAIRS.items():
        result = check_math_amp(pair, yf_pair)
        if result.get("signal"):
            signals.append(pair)
            logger.info(f"SIGNAL: {pair}")
    logger.info(f"Signals: {signals}")

if __name__ == "__main__":
    main()
