#!/usr/bin/env python3
"""
Get Prices
=========
Gets current prices from yfinance.
Usage: python3 get_prices.py
"""
import yfinance as yf
from pathlib import Path

PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "XAUUSD": "GC=F",
}


def main():
    for name, ticker in PAIRS.items():
        t = yf.Ticker(ticker)
        price = t.history(period="1d")
        if len(price) > 0:
            print(f"{name}: {price['Close'].iloc[-1]:.5f}")

if __name__ == "__main__":
    main()
