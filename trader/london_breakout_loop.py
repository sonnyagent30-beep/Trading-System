#!/usr/bin/env python3
"""
London Breakout USDJPY — Specialized Trading Loop
"""
import json, time, logging, threading, sys, os, signal, uuid
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

BRIDGE_URL   = "http://127.0.0.1:9090"
MAGIC        = 20250603
D1_BULL_LEVEL = 160.35
D1_BEAR_LEVEL = 159.80
LONDON_OPEN_HOUR  = 8
LONDON_CLOSE_HOUR = 12
RANGE_END_HOUR    = 9

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("london_breakout")

_state = {
    "status": "idle", "strategy": "London_Breakout_USDJPY",
    "cycle_count": 0, "total_trades": 0, "winning_trades": 0,
    "losing_trades": 0, "d1_direction": "unknown", "d1_confirmed": False,
    "session_status": "waiting", "open_positions": [],
}

def save_state():
    with open("/root/workspace/forex/trader/state.json", "w") as f:
        json.dump(_state, f, indent=2, default=str)


class Bridge:
    def __init__(self, url: str, magic: int):
        self.url = url.rstrip("/"); self.magic = magic

    def _get(self, path: str) -> Optional[Dict]:
        import urllib.request
        try:
            with urllib.request.urlopen(f"{self.url}{path}", timeout=10) as r:
                return json.loads(r.read())
        except Exception as e:
            logger.warning(f"Bridge GET {path}: {e}")
            return None

    def _post(self, path: str, data: Dict) -> Optional[Dict]:
        import urllib.request
        try:
            req = urllib.request.Request(
                f"{self.url}{path}",
                data=json.dumps(data).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read())
        except Exception as e:
            logger.warning(f"Bridge POST {path}: {e}")
            return None

    def get_signals(self) -> List[dict]:
        resp = self._get("/signals")
        if not resp: return []
        return resp.get("signals", [])

    def get_positions(self, symbol: str = "USDJPY") -> List[dict]:
        resp = self._get("/positions")
        if not resp: return []
        return [p for p in resp.get("positions", []) if p.get("symbol") == symbol]

    def queue_order(self, action: str, symbol: str, lot: float, sl: float, tp: float) -> Optional[Dict]:
        return self._post("/queue", {"action": action, "symbol": symbol,
                                     "lot": lot, "sl": sl, "tp": tp,
                                     "comment": "London_Breakout_v1", "magic": self.magic})

def gmt_now() -> datetime:
    return datetime.now(timezone.utc)

def is_in_session() -> bool:
    dt = gmt_now()
    return LONDON_OPEN_HOUR <= dt.hour < LONDON_CLOSE_HOUR

def is_range_eligible() -> bool:
    dt = gmt_now()
    return dt.hour > RANGE_END_HOUR

def is_past_close() -> bool:
    return gmt_now().hour >= LONDON_CLOSE_HOUR

running = True

def signal_handler(sig, frame):
    global running
    logger.info(f"Signal {sig} — shutting down...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    global running
    logger.info("London Breakout USDJPY Loop")
    bridge = Bridge(BRIDGE_URL, MAGIC)
    _state["status"] = "running"
    _state["start_time"] = gmt_now().isoformat()
    save_state()

    trade_executed = False
    trade_ticket = None
    cycle = 0

    while running:
        cycle += 1
        now = gmt_now()
        _state["cycle_count"] = cycle

        if is_past_close():
            logger.info("Session CLOSED — flattening")
            positions = bridge.get_positions()
            for pos in positions:
                bridge._post("/queue", {"action": "close", "ticket": pos.get("ticket")})
            _state["session_status"] = "closed"
            break

        in_session = is_in_session()
        range_eligible = is_range_eligible()

        signals = bridge.get_signals()
        positions = bridge.get_positions()

        logger.info(f"[C{cycle}] session={'OPEN' if in_session else 'CLOSED'} range={'eligible' if range_eligible else 'forming'}")

        if not trade_executed and in_session and range_eligible and signals:
            sig = signals[0]
            action = sig.get("action", "buy").lower()
            price = sig.get("price", 0)
            sl = sig.get("sl", 0)
            tp = sig.get("tp", 0)
            lot = sig.get("volume", 0.01)

            
            if price > 0 and sl > 0:
                res = bridge.queue_order(action, "USDJPY", lot, sl, tp)
                if res:
                    trade_executed = True
                    trade_ticket = res.get("ticket")
                    logger.info(f"Trade executed: {action} USDJPY @ {price}")

        if trade_executed and trade_ticket:
            pos = next((p for p in positions if p.get("ticket") == trade_ticket), None)
            if pos:
                logger.info(f"P&L: ${pos.get('profit', 0):.2f}")

        save_state()
        time.sleep(10)

    logger.info("Loop ended")

if __name__ == "__main__":
    main()
