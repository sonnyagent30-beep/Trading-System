#!/usr/bin/env python3
"""
Signal Evaluator — Evaluates trading signals.
"""
import json
import math

def evaluate_signal(signal, market_data):
    """Evaluate if signal should be executed."""
    result = {"action": "reject", "reason": "", "confidence": 0}
    
    # Check confidence
    conf = signal.get("confidence", 0)
    if conf < 2:
        result["reason"] = "low_confidence"
        return result
    
    # Check R:R
    entry = signal.get("entry_price", 0)
    sl = signal.get("sl", 0)
    tp = signal.get("tp", 0)
    
    if entry > 0 and sl > 0:
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        rr = reward / risk if risk > 0 else 0
        if rr < 2:
            result["reason"] = "insufficient_rr"
            return result
    
    # Check spread
    spread = market_data.get("spread", 0)
    if spread > 3:
        result["reason"] = "spread_too_wide"
        return result
    
    result["action"] = "approve"
    result["reason"] = "all_gates_passed"
    result["confidence"] = conf
    return result

if __name__ == "__main__":
    test_signal = {
        "entry_price": 1.1000,
        "sl": 1.0980,
        "tp": 1.1040,
        "confidence": 3
    }
    test_market = {"spread": 2}
    print(json.dumps(evaluate_signal(test_signal, test_market), indent=2))
