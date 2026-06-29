#!/usr/bin/env python3
"""
Full matrix scan — check all pairs.
"""
import yfinance as yf
import json

SYMBOLS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "EURJPY": "EURJPY=X",
    "GBPJPY": "GBPJPY=X",
    "NZDUSD": "NZDUSD=X",
    "XAUUSD": "GC=F",
}

def scan_all():
    results = {}
    for name, yf_sym in SYMBOLS.items():
        try:
            t = yf.Ticker(yf_sym)
            df = t.history(period='2d', interval='1h')
            if len(df) < 2:
                results[name] = {"error": "no_data"}
                continue
            
            close = float(df['Close'].iloc[-1])
            high = float(df['High'].max())
            low = float(df['Low'].min())
            
            results[name] = {
                "price": round(close, 5),
                "high": round(high, 5),
                "low": round(low, 5),
            }
        except Exception as e:
            results[name] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    print(json.dumps(scan_all(), indent=2))
