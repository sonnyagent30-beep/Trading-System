# Trade Advisor Module — Integration Guide

## Overview

`trade_advisor.py` is an enhanced analytics layer for the MT5 Manager Loop that makes **smarter real-time exit/management decisions** for open positions. It runs every 30 seconds with the existing cycle, but **cannot open new trades**.


---

## Quick Start

### 1. Add to `mt5_manager_loop.py`

In `manage_open_positions()`, add after the trailing SL check:
```python
# After existing trail_sl() calls
if positions:
    from trade_advisor import run_advisor_cycle
    actions = run_advisor_cycle(bridge, state, positions)
    for action in actions:
        logger.info(f"ADVISOR: {action['symbol']} {action['decision'].action} "
                    f"(confidence={action['decision'].confidence:.0%})")
```

### 2. Required Dependencies

All already available on VPS:
- `yfinance` (market data)
- `pandas` (data analysis)
- `numpy` (calculations)


---

## Design Decisions Answered

### 1. What Management Decisions Can the Manager Make?

| Decision | Description | Constraints |
|----------|-------------|-------------|
| `early_exit` | Close position now | Min 10 pips profit, confidence >= 65% |
| `partial_close` | Close 50% of position | Min 20 pips profit, strong trend |
| `tighten_sl` | Move SL in favor | Only improves SL (never worsens), ATR-based |
| `alert_only` | Notify but don't act | Any confidence |
| `hold` | No action | Default |

**Cannot do:**
- Open new trades
- Widen SL against position direction
- Remove TP without justification
- Act during spread protection window

---

### 2. Analytics Modules Per Decision

| Module | Purpose | Indicators Used |
|--------|---------|-----------------|
| `MomentumExhaustionRule` | Detect reversal signs | H4 RSI, H4 ADX |
| `TrendAlignmentRule` | D1 trend alignment check | D1 EMA20 position/direction |
| `VolatilityRegimeRule` | ATR collapse detection | M15 ATR ratio (10 bars) |
| `SessionRiskRule` | NY close/Asia open danger | WAT hour check |
| `SupportResistanceProximityRule` | Near key levels | H4 EMA20 distance |
| `PartialCloseOpportunityRule` | Lock in gains | Profit + ADX + D1 alignment |
| `TimeInTradeRule` | Held too long | Hours open |
| `DynamicSLTightenRule` | ATR-based SL locking | M15 ATR buffer |

---

## Configuration Tuning

Edit `ADVISOR_CONFIG` in `trade_advisor.py`:

```python
ADVISOR_CONFIG = {
    "min_action_confidence": 0.65,
    "action_cooldown_cycles": 6,
    "min_profit_for_exit": 10.0,
    "atr_sl_buffer": 0.5,
    "adx_strong_trend": 25.0,
    "adx_very_strong_trend": 40.0,
    "rsi_overbought": 70.0,
    "rsi_oversold": 30.0,
    "danger_sessions": [21, 22, 0, 1],
}
```
