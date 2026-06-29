# MATH AMP Strategy

## Overview
MATH AMP (Moving Average Trend Hunter) strategy uses EMA crossovers on multiple timeframes.

## Rules
- **BUY**: EMA20 > EMA50 on H4, price above EMA20
- **SELL**: EMA20 < EMA50 on H4, price below EMA20

## Timeframes
- Primary: H4
- Confirmation: D1

## Risk
- 1.5% risk per trade
- SL: 1.5 x ATR(14)
- TP: 3.0 x ATR(14)
