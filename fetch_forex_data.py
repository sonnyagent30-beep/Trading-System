"""
Fetch 5-year daily OHLCV data for EURUSD, GBPUSD, AUDUSD, XAUUSD
using yfinance and save as clean CSV + QC report.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

OUTPUT_DIR = "/root/workspace/forex/data"
TICKERS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "AUDUSD": "AUDUSD=X",
    "XAUUSD": "GC=F",
}

period_from = datetime.now() - timedelta(days=365 * 5)

all_results = {}

for name, yf_ticker in TICKERS.items():
    print(f"\n{'='*60}")
    print(f"  Fetching  {name}  (ticker: {yf_ticker})  …")

    print(f"{'='*60}")

    raw = yf.download(
        yf_ticker,
        start=period_from.strftime("%Y-%m-%d"),
        end=datetime.now().strftime("%Y-%m-%d"),
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if raw.empty:
        print(f"  WARNING: {yf_ticker} returned no data. Skipping.")
        all_results[name] = None
        continue

    # Flatten MultiIndex columns
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [c[0] if c[1] == yf_ticker else f"{c[0]}_{c[1]}"
                       for c in raw.columns]
    raw.columns = [str(c).strip() for c in raw.columns]

    # Keep only OHLCV
    keep = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in raw.columns]
    df = raw[keep].copy()

    df.index = pd.to_datetime(df.index)
    df = df[df.index.notna()]
    df.index = df.index.normalize()
    df.index.name = None
    df.sort_index(inplace=True)

    # QC
    first_d  = df.index[0].date()
    last_d   = df.index[-1].date()
    n_rows   = len(df)
    nan_cnt  = df.isnull().sum()


    print(f"  First row  : {first_d}")
    print(f"  Last row   : {last_d}")
    print(f"  Total rows : {n_rows}")

    # Save
    out_path = f"{OUTPUT_DIR}/{name}.csv"
    df.to_csv(out_path, header=True, index_label="Date")
    print(f"  Saved to   : {out_path}")

    all_results[name] = {
        "path": out_path,
        "first_date": str(first_d),
        "last_date": str(last_d),
        "rows": n_rows,
    }

print(f"\n{'#'*65}")
print(f"  OLCV FETCH — COMPLETE")
print(f"{'#'*65}")
