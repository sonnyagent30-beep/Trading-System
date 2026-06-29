#!/usr/bin/env python3
"""
Gold Check — XAUUSD scanner.
"""
import yfinance as yf
import json

def check_gold():
    try:
        t = yf.Ticker("GC=F")
        df = t.history(period='2d', interval='1h')
        if len(df) < 2:
            return {"error": "no_data"}
        
        current = float(df['Close'].iloc[-1])
        high = float(df['High'].max())
        low = float(df['Low'].min())
        change = current - float(df['Close'].iloc[0])
        
        return {
            "price": round(current, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "change": round(change, 2),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print(json.dumps(check_gold(), indent=2))
