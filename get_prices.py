import yfinance as yf
import json

pairs = ['EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 'GC=F']
results = {}

for p in pairs:
    try:
        t = yf.Ticker(p)
        hist = t.history(period='2d')
        if not hist.empty and len(hist) >= 2:
            curr = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            chg = round((curr - prev) / prev * 100, 3)
            hi = float(hist['High'].iloc[-1])
            lo = float(hist['Low'].iloc[-1])
            results[p] = {
                'price': round(curr, 5),
                'change_pct': chg,
                'high': round(hi, 5),
                'low': round(lo, 5),
                'prev_close': round(prev, 5)
            }
        else:
            results[p] = {'error': 'insufficient data'}
    except Exception as e:
        results[p] = {'error': str(e)}

print(json.dumps(results, indent=2))
