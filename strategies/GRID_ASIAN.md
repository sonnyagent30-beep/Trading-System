# GRID_ASIAN — Asian Session Grid Strategy

**Version:** 1.0
**Created:** 2026-06-09
**Status:** BACKTESTING

## Overview

Grid trading during Asian session (01:00–09:00 WAT) with automatic grid levels. Buy limit orders at lower grid levels, sell limit orders at upper grid levels.

## Core Parameters

| Parameter | Value |
|-----------|-------|
| Grid spacing | 25 pips |
| Grid levels | 5 |
| Max concurrent | 3 |
| Session | Asian (01:00–09:00 WAT) |
| Pairs | EURUSD, GBPUSD, USDJPY |

## Entry Rules

1. Wait for Asian session to open (01:00 WAT)
2. Place initial grid orders at session start price ± grid spacing
3. Add new grid orders every time price crosses a grid level
4. Maximum 3 concurrent positions

## Exit Rules

- Take profit: +25 pips per level
- Stop loss: -50 pips from entry
- Close all at Asian session close (09:00 WAT)

## Risk Management

- Max 2% risk per trade
- Max 6% total Asian session exposure
- No new trades if previous session lost >3%
