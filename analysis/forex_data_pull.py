import yfinance as yf
import json
import os

def pull_forex_data(symbols=None):
    if symbols is None:
        symbols = {
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
    
    results = {}
    for name, yf_sym in symbols.items():
        try:
            t = yf.Ticker(yf_sym)
            hist = t.history(period='5d', interval='1h')
            if not hist.empty:
                results[name] = {
                    "current": float(hist['Close'].iloc[-1]),
                    "high": float(hist['High'].max()),
                    "low": float(hist['Low'].min()),
                    "change": float(hist['Close'].iloc[-1] - hist['Close'].iloc[0]),
                }
        except Exception as e:
            results[name] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    data = pull_forex_data()
    print(json.dumps(data, indent=2))
