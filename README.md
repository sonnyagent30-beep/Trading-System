# Trading-System

Automated FX trading system for MetaTrader 5 (MT5). Architect-Agent-Manager loop with multi-strategy portfolio management.

## Components
- **Architect cycle** — Strategy evaluation, portfolio rebalancing, regime detection
- **Trader loop** — Executes signals via MT5 bridge (port 9090)
- **Scanner** — Multi-timeframe signal generation across FX pairs and XAUUSD
- **Risk manager** — Position sizing, drawdown controls, daily loss limits

## Strategies
- BbRsiRevert, BbSqueeze, BollBreakout, DonchianBreakout, DualThrust
- EMA Cross, EMA Trend 4H, HybridRegime, KeyLevelMiss/Trendline/Reject
- LevelBreakout, LondonBreakout, MACD Divergence/Momentum
- MTF Pullback, RSI MeanReversion, SmaCross, VWAP MeanReversion

## Setup
Copy `.env.example` to `.env` and configure your MT5 bridge credentials.

## Architecture
```
architect_cycle.py  →  trader/  →  MT5 bridge (port 9090)
     ↑                      ↓
     └── manager_reports/  ←── journal/
```

See `SPEC.md`, `forward_test_spec.md`, and `risk_register.md` for full system documentation.
