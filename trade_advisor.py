#!/usr/bin/env python3
"""
Trade Advisor — Enhanced exit/management decisions.
"""
import json
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trade_advisor")

def evaluate_exit(position: dict, market_data: dict) -> dict:
    """
    Evaluate whether to exit a position.
    
    Returns: {
        "action": "hold" | "trail" | "close",
        "reason": str,
        "new_sl": float | None
    }
    """
    entry = position.get("entry_price", 0)
    current = market_data.get("close", 0)
    sl = position.get("sl", 0)
    tp = position.get("tp", 0)
    direction = position.get("direction", "")
    
    if direction == "buy":
        profit_pips = (current - entry) * 10000
        if current >= tp:
            return {"action": "close", "reason": "TP hit", "new_sl": None}
        if current <= sl:
            return {"action": "close", "reason": "SL hit", "new_sl": None}
        # Check for trailing
        if profit_pips >= 20:  # 2:1 RR
            return {"action": "trail", "reason": "2:1 RR", "new_sl": entry}
    else:
        profit_pips = (entry - current) * 10000
        if current <= tp:
            return {"action": "close", "reason": "TP hit", "new_sl": None}
        if current >= sl:
            return {"action": "close", "reason": "SL hit", "new_sl": None}
        if profit_pips >= 20:
            return {"action": "trail", "reason": "2:1 RR", "new_sl": entry}
    
    return {"action": "hold", "reason": "no signal", "new_sl": None}

def evaluate_entry(signal: dict, market_data: dict) -> dict:
    """
    Evaluate whether to enter a trade.
    
    Returns: {
        "action": "enter" | "reject",
        "reason": str,
        "lot_size": float
    }
    """
    # Check confidence
    confidence = signal.get("confidence", 0)
    if confidence < 2:
        return {"action": "reject", "reason": "low confidence", "lot_size": 0}
    
    # Check R:R
    rr = signal.get("rr", 0)
    if rr < 2:
        return {"action": "reject", "reason": "insufficient RR", "lot_size": 0}
    
    # Check spread
    spread = market_data.get("spread", 0)
    max_spread = signal.get("max_spread", 3)
    if spread > max_spread:
        return {"action": "reject", "reason": "spread too wide", "lot_size": 0}
    
    # Calculate lot size
    risk_pct = signal.get("risk_pct", 2)
    balance = signal.get("balance", 10000)
    risk_dollar = balance * (risk_pct / 100)
    lot_size = risk_dollar / 20  # Simplified
    
    return {"action": "enter", "reason": "all gates passed", "lot_size": lot_size}

if __name__ == "__main__":
    # Test
    test_position = {
        "entry_price": 1.1000,
        "sl": 1.0980,
        "tp": 1.1040,
        "direction": "buy"
    }
    test_market = {"close": 1.1020}
    
    result = evaluate_exit(test_position, test_market)
    print(json.dumps(result, indent=2))
