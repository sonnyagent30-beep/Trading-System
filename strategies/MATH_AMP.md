# MATH_AMP — Strategy Specification

**Version:** 1.0
**Created:** 2026-06-09
**Status:** FORWARD TESTING

## Entry Conditions (All must be true)

| ID | Condition | Threshold |
|----|-----------|-----------|
| B1 | D1 EMA20 direction | Falling (SHORT) or Rising (LONG) |
| B2 | H4 pullback zone | Price within 0.5–1.0 ATR of EMA20 |
| B3 | H4 not overextended | Within 1.5× ATR of EMA20 |
| B4 | M15 rejection candle | Close < Open AND Close < EMA20 |
| B5 | M15 ATR momentum | ATR > 0.9× 10 bars ago |
| B6 | Time window | 01:00–21:30 WAT |
| B7 | Spread within limit | ≤ 3× normal for pair |
| B8 | No high-impact news | KILL #1 CLEAR |

## Execution Gates (All mandatory — fail = reject)


| Gate | Rule | Threshold |
|------|------|-----------|
| G1 | Risk:Reward | ≥ 2:1 |
| G2 | Confidence | ≥ 2/5 (base) |
| G3 | H4 ADX | ≥ 22 — MISSING ADX = REJECT |
| G4 | Spread | ≤ 3× normal |
| G5 | Time | 01:00–21:30 WAT |

## D1 Confluence Modifier

| D1 vs H4 | Effect |
|----------|--------|
| D1 confirms H4 | +1 confidence notch |
| D1 contradicts H4 | -1 confidence notch |
| D1 neutral | No change |

**Adjusted C = base C + D1 modifier (capped at 5/5)**
D1 direction is NOT a gate — it is a confidence modifier only.

## Position Sizing

```
Risk_dollar = 2% × ACTUAL_BALANCE × (adjusted_C / 5)
Lot = Risk_dollar / (SL_pips × pip_value_per_minilot)
```
