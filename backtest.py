import os
import sys
import json
import datetime
import argparse

import backtrader as bt
import pandas as pd
import numpy as np
import yfinance as yf

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WORKSPACE)

# Strategy imports would go here
# from strategies.sma_cross import SmaCross

REPORTS_DIR = os.path.join(WORKSPACE, "reports")
DATA_DIR = os.path.join(WORKSPACE, "data")
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Symbol mapping for yfinance
YF_SYMBOL_MAP = {
    "frxEURUSD": "EURUSD=X",
    "frxGBPUSD": "GBPUSD=X",
    "frxUSDJPY": "USDJPY=X",
    "frxAUDUSD": "AUDUSD=X",
    "frxXAUUSD": "GC=F",
}

def fetch_data(symbol: str, days: int = 365) -> pd.DataFrame:
    """Fetch historical OHLCV data via yfinance."""
    yf_symbol = YF_SYMBOL_MAP.get(symbol, symbol)
    cache = os.path.join(DATA_DIR, f"{yf_symbol}.csv")
    if os.path.exists(cache):
        df = pd.read_csv(cache, index_col=0)
        df.index = pd.to_datetime(df.index, utc=True)
        if len(df) > 50:
            return df
    
    ticker = yf.Ticker(yf_symbol)
    df = ticker.history(period=f"{days}d", interval="1h", auto_adjust=True)
    df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
    df.to_csv(cache)
    return df

def compute_metrics(broker_value: list, trades: list):
    """Calculate backtest metrics."""
    values = np.array(broker_value, dtype=float)
    if len(values) < 2:
        return {}
    
    total_return = (values[-1] / values[0]) - 1
    n_trades = len(trades)
    winners = [t for t in trades if t.get("pnlcomm", 0) > 0]
    losers = [t for t in trades if t.get("pnlcomm", 0) <= 0]
    win_rate = len(winners) / n_trades if n_trades else 0
    
    return {
        "total_return_pct": round(total_return * 100, 2),
        "n_trades": n_trades,
        "win_rate_pct": round(win_rate * 100, 2),
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Hermes Forex Backtest Runner")
    parser.add_argument("--strategy", default="ema_cross")
    parser.add_argument("--symbol", default="frxEURUSD")
    parser.add_argument("--days", type=int, default=365)
    args = parser.parse_args()
    
    print(f"Backtest: {args.symbol} | {args.days} days")
    df = fetch_data(args.symbol, args.days)
    print(f"Loaded {len(df)} bars")
