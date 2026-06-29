import yfinance as yf
import json

def get_live_price(symbol: str) -> dict:
    """Get live price for a forex pair."""
    yf_sym = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X",
        "USDJPY": "USDJPY=X",
        "AUDUSD": "AUDUSD=X",
        "XAUUSD": "GC=F",
    }.get(symbol, symbol)
    
    try:
        t = yf.Ticker(yf_sym)
        hist = t.history(period='1d', interval='5m')
        if hist.empty:
            return {"error": "no data"}
        
        curr = hist['Close'].iloc[-1]
        high = hist['High'].max()
        low = hist['Low'].min()
        return {
            "symbol": symbol,
            "price": round(float(curr), 5),
            "high": round(float(high), 5),
            "low": round(float(low), 5),
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    for sym in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]:
        print(json.dumps(get_live_price(sym), indent=2))
