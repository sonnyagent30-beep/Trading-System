#!/usr/bin/env python3
"""
Fetch Forex Data
==============
Fetches forex data from yfinance.
Usage: python3 fetch_forex_data.py --pair EURUSD --days 365
"""
import argparse, sys, os
import yfinance as yf
import pandas as pd
from pathlib import Path

WORKSPACE = Path("/root/workspace/forex")
DATA_DIR = WORKSPACE / "data"
DATA_DIR.mkdir(exist_ok=True)

PAIR_MAP = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "XAUUSD": "GC=F",
}

def fetch(pair: str, days: int = 365):
    yf_pair = PAIR_MAP.get(pair, pair)
    print(f"Fetching {yf_pair} ({days} days)...")
    
    ticker = yf.Ticker(yf_pair)
    df = ticker.history(period=f"{days}d", interval="1h", auto_adjust=True)
    
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    
    out_path = DATA_DIR / f"{yf_pair}.csv"
    df.to_csv(out_path)
    print(f"Saved {len(df)} bars to {out_path}")
    
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pair", default="EURUSD")
    parser.add_argument("--days", type=int, default=365)
    args = parser.parse_args()
    
    fetch(args.pair, args.days)

if __name__ == "__main__":
    main()
