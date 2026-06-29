# Forward-Test Spec — Setup 1 x GBPUSD
*Generated: 2026-06-06*

---

## Strategy: Keylevel + Trendline (DANNION SNR Setup 1)


### Core Rules
- **BUY**: D1 bull (EMA20 > EMA50 on D1) + price at recent swing LOW + price DEPARTED bullish from level (confirms support holds) + price within 60 pips of level + bullish candle on retest
- **SELL**: D1 bear (EMA20 < EMA50 on D1) + price at recent swing HIGH + bearish candle on retest

### Entry
- Confirm D1 direction: EMA20 > EMA50 (bull) / EMA20 < EMA50 (bear)
- Identify recent swing low/high: lowest/highest of last 20 bars, aged 5-35 bars back
- Verify price DEPARTED from level (closed beyond it = level confirmed valid)
- Wait for price within 60 pips of that level + same-direction candle
- Size: 2% risk per trade

### Stop Loss / Take Profit
- **SL**: 1.5 x ATR(14)
- **TP**: 3.0 x ATR(14)
- **Trailing**: close at breakeven when profit = 1:1 risk

### Filters / Gate
- Minimum ATR: 8 pips (no trades in low volatility)
- Level must not have been broken in last 5 bars
- No trades on USDJPY (backtest showed 0 trades — volatility profile incompatible)

### Backtest Results (5-year, daily bars)
| Metric | Value |
|--------|-------|
| Pair | GBPUSD |
| Period | 5 years |
| Trades | 19 |
| Win Rate | 73.68% |
| Profit Factor | 6.128 |
| Max Drawdown | -34.78% |
| Return | +21.22% |
| Final Value | $60.61 |

---

## Live Forward-Test Parameters

| Parameter | Value |
|-----------|-------|
| Pair | GBPUSD |
| Direction | BUY only (D1 bull confirmed) |
| Risk | 2% per trade |
| SL | 1.5 x ATR(14) |
| TP | 3.0 x ATR(14) |
| Trailing | Close at BE when profit = 1:1 risk |
| Magic Number | 20250603 |
| Bridge Port | 9090 |
| Architect | posts signals via bridge |
| Trader | polls bridge every 30s |

---

## Bridge Communication Protocol

### Architect -> Bridge (POST /queue)
```json
{
  "action": "buy",
  "symbol": "GBPUSD",
  "volume": 0.01,
  "sl": "1.3150",
  "tp": "1.3200",
  "setup": "KeylevelTrendline",
  "entry_price": "1.3155",
  "confidence": 0.75,
  "rr": 3.0,
  "comment": "KLT-GBPUSD-Test",
  "magic": 20250603
}
```

### Trader -> Bridge (GET /signals)
Polls every 30 seconds. Gets pending signals, executes if gate passed.

### Bridge -> MT5 EA (GET /next)
EA reads pending commands and executes on MT5.

### EA -> Bridge (POST /result)
Posts trade ticket, open/close prices, PnL after fill.

