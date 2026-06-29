#!/usr/bin/env python3
"""
MATH_AMP Scanner — Market opportunity scanner.
Scans multiple pairs and timeframes for entry signals.
"""
import yfinance as yf
import json
import pandas as pd
from datetime import datetime, timezone

SYMBOLS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "GBPJPY=X"]
TIMEFRAMES = ["1h", "4h", "1d"]

def get_atr(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def scan_pair(symbol):
    try:
        t = yf.Ticker(symbol)
        df = t.history(period='5d', interval='1h')
        if len(df) < 20:
            return {"status": "insufficient_data"}
        
        # Calculate indicators
        df['EMA20'] = df['Close'].ewm(span=20).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        df['ATR'] = get_atr(df)
        
        current = df['Close'].iloc[-1]
        ema20 = df['EMA20'].iloc[-1]
        ema50 = df['EMA50'].iloc[-1]
        atr = df['ATR'].iloc[-1]
        
        # Direction
        direction = "bull" if ema20 > ema50 else "bear"
        
        # Pullback check
        dist_from_ema = abs(current - ema20) / atr
        in_pullback = dist_from_ema < 1.5
        
        return {
            "direction": direction,
            "ema20": round(ema20, 5),
            "ema50": round(ema50, 5),
            "atr": round(atr, 5),
            "in_pullback": in_pullback,
            "dist_from_ema_pct": round(dist_from_ema, 2),
        }
    except Exception as e:
        return {"error": str(e)}

def main():
    results = {}
    for sym in SYMBOLS:
        name = sym.split("=")[0]
        results[name] = scan_pair(sym)
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
