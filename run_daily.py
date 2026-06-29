"""
Daily backtest runner.
Runs all strategies against EURUSD and Gold data.
"""
import sys, json, os
sys.path.insert(0, '/root/workspace/forex')
sys.path.insert(0, '/root/workspace/forex/strategies')
import backtrader as bt, pandas as pd

WORKSPACE = '/root/workspace/forex'
DATA_DIR  = f'{WORKSPACE}/data'

# Strategy imports
# from strategies.sma_cross import SmaCross
# from strategies.ema_cross import EmaCross

def load_data(symbol):
    df = pd.read_csv(f'{DATA_DIR}/{symbol}', index_col=0)
    df.index = pd.to_datetime(df.index, utc=True)
    return df[['Open','High','Low','Close','Volume']].dropna()

def run_once(cls, df):
    feed = bt.feeds.PandasData(
        dataname=df, open='Open', high='High', low='Low',
        close='Close', volume='Volume',
        timeframe=bt.TimeFrame.Days, compression=1,
    )
    c = bt.Cerebro()
    c.adddata(feed)
    c.addstrategy(cls)
    c.broker.setcash(50)
    c.broker.setcommission(commission=0.0001, leverage=100)
    c.addanalyzer(bt.analyzers.TradeAnalyzer,  _name='ta')
    res = c.run()
    return c.broker.getvalue()

if __name__ == "__main__":
    print("Daily backtest runner")
    print("Load data from data/ directory and run strategies")
