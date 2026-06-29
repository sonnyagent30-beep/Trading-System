import yfinance as yf
import json

SYMBOLS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "EURJPY=X", "GBPJPY=X", "NZDUSD=X", "GC=F"]

def check_spreads():
    results = {}
    for sym in SYMBOLS:
        try:
            t = yf.Ticker(sym)
            df = t.history(period='1d', interval='5m')
            if len(df) > 0:
                spread = (df['High'].iloc[-1] - df['Low'].iloc[-1]) * 10000
                results[sym] = round(spread, 2)
        except:
            results[sym] = None
    return results

if __name__ == "__main__":
    print(json.dumps(check_spreads(), indent=2))
