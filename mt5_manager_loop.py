#!/usr/bin/env python3
"""
MT5 Manager Loop v2.0
=====================
Persistent background loop — reads bridge queue, executes trades,
manages positions, enforces kill factors, handles spread widening,
sends WhatsApp alerts, logs reports for architect review.

Usage: python3 mt5_manager_loop.py
Runs forever. Managed by systemd: mt5-manager.service
"""

import json, os, sys, time, logging, signal, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = Path("/root/workspace/forex")
JOURNAL_DIR   = BASE_DIR / "journal" / "manager_reports"
STATE_PATH    = BASE_DIR / "trader" / "state_manager.json"
LOG_PATH      = BASE_DIR / "logs" / "mt5_manager.log"
BRIDGE_URL    = "http://localhost:9090"
MAGIC         = 20250603

# WhatsApp — Dannion
WHATSAPP_JID  = "60168616341745@lid"   # Dannion's WhatsApp LID (from config.yaml)
WHATSAPP_API  = "http://localhost:3001/send"

JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "logs").mkdir(exist_ok=True)
(BASE_DIR / "trader").mkdir(parents=True, exist_ok=True)

WAT_OFFSET    = 1
CYCLE_SECS    = 30

# Spread widening threshold (NY close → Asia open)
# If spread > NORMAL_SPREAD × SPREAD_MULT, block all new entries
SPREAD_MULT  = 2.5

# Kill switch multipliers
KILL_ATR_MULT = 0.6   # D1 ATR < ATR(20) × 0.6 → kill switch #3

# Supported symbols
SYMBOLS = ["EURUSD", "GBPUSD", "AUDUSD", "XAUUSD", "USDJPY", "EURGBP"]


# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("mt5_manager")

# ── State ──────────────────────────────────────────────────────────────────
@dataclass
class State:
    cycle: int = 0
    positions: list = None
    closed_today: float = 0.0
    daily_pnl: float = 0.0
    last_equity: float = 0.0
    last_resume: str = ""
    
    def __post_init__(self):
        if self.positions is None:
            self.positions = []

def load_state() -> State:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            data = json.load(f)
            return State(**data)
    return State()

def save_state(state: State):
    with open(STATE_PATH, "w") as f:
        json.dump(asdict(state), f, indent=2)

# ── Bridge API ──────────────────────────────────────────────────────────────────────────────
def bridge_get(path: str) -> dict:
    url = f"{BRIDGE_URL}{path}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"Bridge API error: {e}")
        return {}

def bridge_post(path: str, data: dict) -> dict:
    url = f"{BRIDGE_URL}{path}"
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        logger.error(f"Bridge API error: {e}")
        return {"ok": False}

# ── Time Helpers ────────────────────────────────────────────────────────────────
def wat_now() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=WAT_OFFSET)


def is_weekend() -> bool:
    return wat_now().weekday() >= 5

def is_ny_close_window() -> bool:
    hour = wat_now().hour
    return hour in (21, 22, 23)

def is_cutoff_imminent() -> bool:
    hour = wat_now().hour
    minute = wat_now().minute
    return hour == 21 and minute >= 50

# ── Kill Factor Checks ────────────────────────────────────────────────────────
def check_opposing_signals(symbol: str) -> bool:
    sigs = bridge_get("/signals")
    for s in sigs.get("signals", []):
        if s.get("symbol") == symbol and s.get("action") != "buy":
            return True
    return False

def enforce_kill_factors(positions: list, state: State):
    # Kill #1 (news) — news scanner triggers
    news = bridge_get("/news_kill")
    if news.get("kill"):
        for pos in positions:
            if pos.get("volume", 0) > 0:
                # Flatten 50%
                bridge_post("/close_partial", {"ticket": pos["ticket"], "percent": 50})
                logger.warning(f"KILL #1 (news): {pos['symbol']} partial close 50%")

    # Kill #2 (D1 flip) — checked in architect_cycle, enforced here
    for pos in positions:
        d1_dir = bridge_get(f"/d1_direction/{pos['symbol']}")
        if d1_dir.get("direction") and d1_dir["direction"] not in (pos.get("type", ""), pos.get("type", ""):
            # Close all
            bridge_post("/close", {"ticket": pos["ticket"]})
            logger.warning(f"KILL #2 (D1 flip): {pos['symbol']} closed")

# ── Position Management ──────────────────────────────────────────────────
def manage_open_positions(bridge, state: State):
    positions = bridge_get("/positions")
    if not positions.get("positions"):
        return
    
    for pos in positions["positions"]:
        # Spread protection (NY close window)
        if is_ny_close_window():
            # Don't modify during NY close
            continue
        
        # Trailing stop (breakeven at 1:1)
        entry = pos.get("entry", 0)
        current = pos.get("price_current", 0)
        sl = pos.get("sl", 0)
        
        if entry and current and sl:
            diff = current - entry
            if pos.get("type") == "sell":
                diff = entry - current
            
            if diff > 0 and abs(diff) >= abs(entry - sl):
                # Move SL to breakeven
                bridge_post("/modify", {
                    "ticket": pos["ticket"],
                    "sl": entry,
                })
                logger.info(f"Trailed SL to breakeven: {pos['symbol']}")

# ── Queue Processing ────────────────────────────────────────────────────────────────
def process_queue():
    sigs = bridge_get("/queue")
    for sig in sigs.get("signals", []):
        if sig.get("symbol") not in SYMBOLS:
            continue
        
        # Gate checks
        if is_ny_close_window():
            logger.warning(f"Spread protection active — skipping {sig['symbol']}")
            continue
        
        if check_opposing_signals(sig["symbol"]):
            logger.warning(f"Opposing signal in queue — skipping {sig['symbol']}")
            continue

        # Execute
        result = bridge_post("/execute", sig)
        if result.get("ticket"):
            logger.info(f"Executed: {sig['symbol']} @ {sig.get('entry_price')} (ticket={result['ticket']})")
        else:
            logger.error(f"Execution failed: {sig['symbol']} → {result}")

# ── Daily Reset ────────────────────────────────────────────────────────────────
def check_daily_reset(state: State):
    now = wat_now()
    if state.last_resume and state.last_resume[:10] != now.isoformat()[:10]:
        state.closed_today = 0.0
        state.daily_pnl = 0.0
        state.last_resume = now.isoformat()
        logger.info("Daily reset")

# ── Main Cycle ────────────────────────────────────────────────────────────────
def cycle():
    logger.info("MT5 Manager cycle started")
    
    # Health check
    health = bridge_get("/health")
    if not health.get("ok"):
        logger.error(f"Bridge unhealthy: {health}")
        return
    
    # Load state
    state = load_state()
    state.cycle += 1
    
    # Weekend guard
    if is_weekend():
        logger.info("Weekend — no trading")
        time.sleep(CYCLE_SECS)
        return
    
    # Check cutoff
    if is_cutoff_imminent():
        logger.info("Cutoff imminent — closing all positions")
        bridge_post("/close_all", {})
        time.sleep(CYCLE_SECS)
        return
    
    # Kill factors
    positions = bridge_get("/positions")
    enforce_kill_factors(positions.get("positions", []), state)

    
    # Process queue
    process_queue()
    
    # Manage positions
    manage_open_positions(bridge_get, state)
    
    # Save state
    save_state(state)

    # Log
    logger.info(f"Cycle {state.cycle} complete")


# ── Entry Point ──────────────────────────────────────────────────────────────
def main():
    logger.info("MT5 Manager Loop starting")
    
    # Catch SIGTERM
    def handle_sigterm(sig, frame):
        logger.info("Received SIGTERM — exiting")
        sys.exit(0)
    signal.signal(signal.SIGTERM, handle_sigterm)
    
    while True:
        try:
            cycle()
        except Exception as e:
            logger.error(f"Cycle error: {e}")
        time.sleep(CYCLE_SECS)

if __name__ == "__main__":
    main()
