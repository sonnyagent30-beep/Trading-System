#!/usr/bin/env python3
"""
XAUUSD Check — Gold scanner.
"""
import yfinance as yf
import json

def check_xauusd():
    try:
        t = yf.Ticker("GC=F")
        hist = t.history(period='1d')
        if hist.empty:
            return {"error": "no_data"}
        
        price = float(hist['Close'].iloc[-1])
        return {
            "symbol": "XAUUSD",
            "price": round(price, 2),
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(json.dumps(check_xauusd(), indent=2))
