#!/usr/bin/env python3
"""
Production-Grade Persistent Forex-Trader Agent Loop
"""
import json, time, logging, threading, sys, os, signal
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from enum import Enum

CONFIG_PATH = "/root/workspace/forex/trader/config.json"
STATE_PATH = "/root/workspace/forex/trader/state.json"
JOURNAL_PATH = "/root/workspace/forex/trader/journal.jsonl"
LOG_PATH = "/root/workspace/forex/trader/trader.log"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("forex_trader")

class TradeDirection(Enum):
    BUY = "buy"; SELL = "sell"

@dataclass
class Signal:
    id: str; symbol: str; direction: TradeDirection; entry_price: float
    timestamp: str; strategy: str; confidence: float
    stop_loss: float; take_profit: float; volume: float

@dataclass
class Position:
    ticket: int; symbol: str; direction: TradeDirection; entry_price: float
    current_price: float; volume: float; stop_loss: float; take_profit: float
    magic: int; open_time: str; profit: float; reason: str

def load_config() -> Dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f: return json.load(f)
    return {"bridge_url": "http://84.247.132.12:9090", "magic": 20250603,
            "cycle_seconds": 30, "max_risk_per_trade": 0.02, "default_stop_loss_pips": 20,
            "default_take_profit_pips": 40, "max_open_positions": 5}

_state = {
    "status": "idle", "cycle_count": 0, "total_trades": 0, "winning_trades": 0,
    "losing_trades": 0, "pending_signals": [], "open_positions": [],
    "last_cycle_time": None, "last_trade_time": None, "whatsapp_enabled": True,
    "start_time": None
}

def save_state():
    with open(STATE_PATH, "w") as f:
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

    def get_signals(self) -> List[Signal]:
        resp = self._get("/signals")
        if not resp: return []
        signals = []
        for item in resp.get("signals", []):
            try:
                action = item.get("action", "buy").lower()
                signals.append(Signal(
                    id=item.get("id", ""), symbol=item.get("symbol", ""),
                    direction=TradeDirection.BUY if action in ("buy","long") else TradeDirection.SELL,
                    entry_price=float(item.get("price", item.get("entry_price", 0))),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    strategy=item.get("setup", item.get("strategy", "signal")),
                    confidence=float(item.get("confidence", 0.5)),
                    stop_loss=float(item.get("sl", 0)),
                    take_profit=float(item.get("tp", 0)),
                    volume=float(item.get("volume", item.get("lot", 0.01))),
                ))
            except: pass
        return signals

    def get_positions(self) -> List[Position]:
        resp = self._get("/positions")
        if not resp: return []
        positions = []
        for item in resp.get("positions", []):
            try:
                t = item.get("type", "BUY").upper()
                positions.append(Position(
                    ticket=int(item.get("ticket", 0)), symbol=item.get("symbol", ""),
                    direction=TradeDirection.BUY if t == "BUY" else TradeDirection.SELL,
                    entry_price=float(item.get("open_price", 0)),
                    current_price=float(item.get("price", 0)),
                    volume=float(item.get("volume", 0.01)),
                    stop_loss=float(item.get("sl", 0)), take_profit=float(item.get("tp", 0)),
                    magic=int(item.get("magic", self.magic)),
                    open_time=item.get("open_time", ""),
                    profit=float(item.get("profit", 0)), reason=item.get("reason", ""),
                ))
            except: pass
        return positions

    def execute(self, direction: str, symbol: str, volume: float, sl: float, tp: float) -> Optional[Dict]:
        return self._post("/queue", {"action": direction, "symbol": symbol,
                                     "volume": volume, "sl": sl, "tp": tp})

    def close(self, ticket: int) -> Optional[Dict]:
        return self._post("/queue", {"action": "close", "ticket": ticket})

    def modify(self, ticket: int, sl: float, tp: float) -> Optional[Dict]:
        return self._post("/queue", {"action": "modify", "ticket": ticket, "sl": sl, "tp": tp})


class Reasoner:
    def __init__(self, cfg: Dict): self.cfg = cfg

    def evaluate(self, sig: Signal, positions: List[Position]) -> str:
        max_pos = self.cfg.get("max_open_positions", 5)
        open_count = len([p for p in positions])
        syms = [p.symbol for p in positions]
        rr_min = 2.0

        if open_count >= max_pos:
            return f"REJECT: max positions ({max_pos})"
        if sig.symbol in syms:
            return f"REJECT: {sig.symbol} already held"
        if sig.volume < 0.01 or sig.volume > 0.10:
            return f"REJECT: volume {sig.volume} outside safe range"
        if sig.confidence < 0.5:
            return f"REJECT: confidence {sig.confidence} below 0.5"
        if sig.stop_loss > 0 and sig.entry_price > 0:
            sl = abs(sig.entry_price - sig.stop_loss)
            tp = abs(sig.take_profit - sig.entry_price) if sig.direction == TradeDirection.BUY else abs(sig.entry_price - sig.take_profit)
            rr = tp / sl if sl > 0 else 0
            if rr < rr_min:
                return f"REJECT: RR={rr:.2f}:1 < {rr_min}:1"
        return f"APPROVE: {sig.direction.value.upper()} {sig.symbol}"

running = True

def signal_handler(sig, frame):
    global running
    logger.info(f"Signal {sig}, shutting down...")
    running = False
    _state["status"] = "stopped"
    save_state()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    global running
    cfg = load_config()
    bridge = Bridge(cfg["bridge_url"], cfg["magic"])
    reasoner = Reasoner(cfg)
    cycle_sec = cfg.get("cycle_seconds", 30)

    _state["status"] = "running"
    _state["start_time"] = datetime.now(timezone.utc).isoformat()
    save_state()
    logger.info("🚀 FOREX TRADER STARTING")

    while running:
        cycle_start = time.time()
        _state["cycle_count"] += 1
        save_state()

        signals = bridge.get_signals()
        logger.info(f"Cycle {_state['cycle_count']}: signals={len(signals)}")

        positions = bridge.get_positions()
        _state["open_positions"] = [asdict(p) for p in positions]
        logger.info(f"Positions: {len(positions)}")

        for sig in signals:
            decision = reasoner.evaluate(sig, positions)
            logger.info(f"Signal {sig.symbol}: {decision}")

            if decision.startswith("APPROVE"):
                res = bridge.execute(sig.direction.value, sig.symbol, sig.volume,
                                     sig.stop_loss, sig.take_profit)
                if res:
                    logger.info(f"Trade executed: {sig.direction.value.upper()} {sig.symbol}")
                    _state["total_trades"] += 1
                    _state["last_trade_time"] = datetime.now(timezone.utc).isoformat()
                    save_state()

        elapsed = time.time() - cycle_start
        sleep_time = max(1, cycle_sec - elapsed)
        time.sleep(sleep_time)

    logger.info("Trader stopped")

if __name__ == "__main__":
    main()
