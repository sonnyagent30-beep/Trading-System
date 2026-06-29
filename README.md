# Trading-System

Forex trading system with automated trading, backtesting, and trade management.

## Overview

This is a comprehensive forex trading system that includes:

- **Architect**: Signal generation based on technical analysis
- **Trader**: Trade execution and management
- **Manager**: Real-time position monitoring and risk management
- **Trade Advisor**: Enhanced exit/management decisions
- **Backtest**: Historical strategy testing
- **Scanner**: Market opportunity detection

## Key Files

| File | Purpose |
|------|---------|
| `architect_cycle.py` | Signal generation cycle |
| `mt5_manager_loop.py` | Position management loop |
| `trade_advisor.py` | Smart exit decisions |
| `backtest.py` | Historical backtesting |
| `fetch_forex_data.py` | Data fetching via yfinance |
| `news_scanner.py` | News-based kill factor detection |
| `config.yaml` | System configuration |

## Configuration

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `config.yaml` to configure:
- Risk management parameters
- Trading pairs
- Broker settings
- Timeframes

## Usage

### Run Daily Cycle

```bash
python run_daily.py
```

### Run Backtest

```bash
python backtest.py --strategy ema_cross --symbol EURUSD --from 2020-01-01
```


### Run Manager

```bash
python mt5_manager_loop.py
```

## Requirements


- Python 3.8+
- yfinance
- pandas
- numpy
- backtrader
- requests

## License

MIT
