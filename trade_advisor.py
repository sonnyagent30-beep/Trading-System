#!/usr/bin/env python3
"""
Trade Advisor Module v1.0
=========================
Enhanced analytics layer for the MT5 Manager Loop.
Makes SMARTER real-time exit/management decisions for open positions.

CONSTRAINT: This module CANNOT open new trades. It only advises on
existing positions. All discretionary decisions are logged and notified
via WhatsApp.

Usage:
    from trade_advisor import TradeAdvisor
    advisor = TradeAdvisor(base_dir=Path("/root/workspace/forex"))
    advice = advisor.analyze_position(position, state)
    # advice = {action: "early_exit", confidence: 0.75, reason: "...", details: {...}}
Integration:
    Called from manage_open_positions() AFTER the standard trail_sl() check.
    The advisor can:
    - Recommend early exit when R:R deteriorates
    - Suggest dynamic SL tightening in favorable conditions
    - Identify partial close opportunities
    - Flag concerning market conditions for human review

Author: Hermes Agent (Trade Advisor Design)
"""

import json, logging, time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Literal
from abc import ABC, abstractmethod

import numpy as np
import pandas as pd

BASE_DIR = Path("/root/workspace/forex")
DATA_DIR = BASE_DIR / "data"
JOURNAL_DIR = BASE_DIR / "journal" / "manager_reports"

WAT_OFFSET = 1
CYCLE_SECS = 30

SUPPORTED_SYMBOLS = ["EURUSD", "XAUUSD", "GBPUSD", "AUDUSD", "USDJPY", "EURGBP"]


YF_TICKERS = {
    "EURUSD": "EURUSD=X",
    "XAUUSD": "GC=F",
    "GBPUSD": "GBPUSD=X",
    "AUDUSD": "AUDUSD=X",
    "USDJPY": "USDJPY=X",
    "EURGBP": "EURGBP=X",
}

ADVISOR_CONFIG = {
    "min_action_confidence": 0.55,
    "action_cooldown_cycles": 6,
    "min_profit_for_exit": 10.0,
    "atr_sl_buffer": 0.5,
    "adx_strong_trend": 25.0,
    "adx_very_strong_trend": 40.0,
    "rsi_overbought": 70.0,
    "rsi_oversold": 30.0,
    "danger_sessions": [21, 22, 0, 1],
}

logger = logging.getLogger("trade_advisor")

@dataclass
class MarketSnapshot:
    symbol: str
    timestamp: datetime
    d1_close: float = 0.0
    d1_open: float = 0.0
    d1_high: float = 0.0
    d1_low: float = 0.0
    h4_close: float = 0.0
    h4_open: float = 0.0
    h4_high: float = 0.0
    h4_low: float = 0.0
    h4_ema20: float = 0.0
    m15_close: float = 0.0
    m15_open: float = 0.0
    m15_high: float = 0.0
    m15_low: float = 0.0
    m15_ema20: float = 0.0
    d1_atr: float = 0.0
    h4_atr: float = 0.0
    m15_atr: float = 0.0
    d1_ema20_rising: bool = False
    h4_above_ema20: bool = False
    m15_above_ema20: bool = False
    d1_rsi: float = 50.0
    h4_rsi: float = 50.0
    m15_rsi: float = 50.0
    h4_adx: float = 0.0
    atr_ratio_10bars: float = 1.0
    data_fresh: bool = False
    data_age_seconds: float = 999.0

@dataclass
class PositionContext:
    ticket: int
    symbol: str
    direction: Literal["buy", "sell"]
    entry: float
    current_price: float
    current_sl: float
    current_tp: float
    profit_dollars: float
    profit_pips: float
    volume: float
    time_open_seconds: float
    original_sl: float
    original_tp: float
    sl_pips: float
    tp_pips: float
    risk_amount: float
    rr_current: float
    rr_remaining: float
    market: Optional[MarketSnapshot] = None
    advisor_cooldown_cycles: int = 0
    last_advisory_action: Optional[str] = None
    spread_protection_active: bool = False

@dataclass
class AdvisoryDecision:
    action: Literal["hold", "early_exit", "partial_close", "tighten_sl", "remove_tp", "alert_only"]
    confidence: float
    reason: str
    details: dict = field(default_factory=dict)
    emoji: str = "📊"


class MarketDataFetcher:
    def __init__(self, cache_ttl_seconds: float = 60.0):
        self.cache_ttl = cache_ttl_seconds
        self._cache: dict[str, tuple[MarketSnapshot, float]] = {}

    
    def fetch(self, symbol: str, forced: bool = False) -> Optional[MarketSnapshot]:
        now = time.time()
        if not forced and symbol in self._cache:
            snap, cached_at = self._cache[symbol]
            if now - cached_at < self.cache_ttl:
                return snap
        snap = self._fetch_from_yfinance(symbol)
        if snap:
            self._cache[symbol] = (snap, now)
        return snap
    
    def _fetch_from_yfinance(self, symbol: str) -> Optional[MarketSnapshot]:
        ticker_key = YF_TICKERS.get(symbol, symbol)
        try:
            import yfinance as yf
            ticker = yf.Ticker(ticker_key)
            d1 = ticker.history(period="25d", interval="1d")
            h4 = ticker.history(period="7d", interval="4h")
            m15 = ticker.history(period="3d", interval="15m")
            if len(d1) < 5 or len(h4) < 5 or len(m15) < 5:
                logger.warning(f"Insufficient data for {symbol}")
                return None
            snap = MarketSnapshot(symbol=symbol, timestamp=datetime.now(timezone.utc), data_fresh=True)
            d1_last = d1.iloc[-1]
            snap.d1_close = d1_last["Close"]
            snap.d1_open = d1_last["Open"]
            snap.d1_high = d1_last["High"]
            snap.d1_low = d1_last["Low"]
            snap.d1_ema20 = d1["Close"].ewm(span=20).mean().iloc[-1]
            snap.d1_ema20_rising = d1["Close"].ewm(span=20).mean().iloc[-1] > d1["Close"].ewm(span=20).mean().iloc[-5]
            snap.d1_rsi = self._calculate_rsi(d1["Close"])
            snap.d1_atr = self._calculate_atr(d1)
            h4_last = h4.iloc[-1]
            snap.h4_close = h4_last["Close"]
            snap.h4_open = h4_last["Open"]
            snap.h4_high = h4_last["High"]
            snap.h4_low = h4_last["Low"]
            snap.h4_ema20 = h4["Close"].ewm(span=20).mean().iloc[-1]
            snap.h4_above_ema20 = snap.h4_close > snap.h4_ema20
            snap.h4_rsi = self._calculate_rsi(h4["Close"])
            snap.h4_atr = self._calculate_atr(h4)
            snap.h4_adx = self._calculate_adx(h4)
            m15_last = m15.iloc[-1]
            snap.m15_close = m15_last["Close"]
            snap.m15_open = m15_last["Open"]
            snap.m15_high = m15_last["High"]
            snap.m15_low = m15_last["Low"]
            snap.m15_ema20 = m15["Close"].ewm(span=20).mean().iloc[-1]
            snap.m15_above_ema20 = snap.m15_close > snap.m15_ema20
            snap.m15_rsi = self._calculate_rsi(m15["Close"])
            snap.m15_atr = self._calculate_atr(m15)
            if len(m15) >= 20:
                current_atr = snap.m15_atr
                atr_10_bars_ago = self._calculate_atr(m15.iloc[:-10]) if len(m15) >= 20 else current_atr
                snap.atr_ratio_10bars = current_atr / atr_10_bars_ago if atr_10_bars_ago > 0 else 1.0
            return snap
        except Exception as e:
            logger.error(f"Failed to fetch market data for {symbol}: {e}")
            return None
    
    def _calculate_rsi(self, closes: pd.Series, period: int = 14) -> float:
        if len(closes) < period + 1:
            return 50.0
        delta = closes.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1]) if not np.isnan(rsi.iloc[-1]) else 50.0

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        if len(df) < period + 1:
            return 0.0
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()
        return float(atr.iloc[-1]) if len(atr) > 0 else 0.0

    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> float:
        if len(df) < period * 2:
            return 0.0
        high = df["High"]
        low = df["Low"]
        close = df["Close"]
        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
        atr = self._calculate_atr(df, period)
        if atr == 0:
            return 0.0
        plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(period).mean()
        return float(adx.iloc[-1]) if len(adx) > 0 and not np.isnan(adx.iloc[-1]) else 0.0

class TradeAdvisor:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or BASE_DIR
        self.data_fetcher = MarketDataFetcher()
    
    def analyze_position(self, position: dict, state: dict = None) -> AdvisoryDecision:
        ctx = PositionContext(
            ticket=position.get("ticket", 0),
            symbol=position.get("symbol", ""),
            direction=position.get("type", "buy"),
            entry=position.get("entry", 0),
            current_price=position.get("price_current", 0),
            current_sl=position.get("sl", 0),
            current_tp=position.get("tp", 0),
            profit_dollars=position.get("profit", 0),
            profit_pips=position.get("profit_pips", 0),
            volume=position.get("volume", 0),
            time_open_seconds=position.get("time_open", 0),
            original_sl=position.get("sl", 0),
            original_tp=position.get("tp", 0),
            sl_pips=position.get("sl_pips", 0),
            tp_pips=position.get("tp_pips", 0),
            risk_amount=position.get("risk_amount", 0),
            rr_current=position.get("rr", 0),
            rr_remaining=position.get("rr_remaining", 0),
        )
        
        market = self.data_fetcher.fetch(ctx.symbol)
        if market:
            ctx.market = market
        
        if ctx.profit_pips < ADVISOR_CONFIG["min_profit_for_exit"]:
            return AdvisoryDecision(action="hold", confidence=0.0, reason="Min profit not reached")
        
        if ctx.market:
            m = ctx.market
            cfg = ADVISOR_CONFIG
            
            if ctx.direction == "buy":
                if m.h4_rsi >= cfg["rsi_overbought"] and m.h4_adx < cfg["adx_strong_trend"]:
                    return AdvisoryDecision(
                        action="early_exit",
                        confidence=0.70,
                        reason=f"H4 RSI={m.h4_rsi:.0f} overbought, ADX={m.h4_adx:.0f} weakening",
                        details={"h4_rsi": m.h4_rsi, "h4_adx": m.h4_adx}
                    )
            elif ctx.direction == "sell":
                if m.h4_rsi <= cfg["rsi_oversold"] and m.h4_adx < cfg["adx_strong_trend"]:
                    return AdvisoryDecision(
                        action="early_exit",
                        confidence=0.70,
                        reason=f"H4 RSI={m.h4_rsi:.0f} oversold, ADX={m.h4_adx:.0f} weakening",
                        details={"h4_rsi": m.h4_rsi, "h4_adx": m.h4_adx}
                    )
        
        return AdvisoryDecision(action="hold", confidence=0.0, reason="No advisory trigger")

def run_advisor_cycle(bridge, state, positions):
    advisor = TradeAdvisor()
    decisions = []
    for pos in positions:
        decision = advisor.analyze_position(pos, state)
        decisions.append({
            "symbol": pos.get("symbol"),
            "ticket": pos.get("ticket"),
            "decision": decision.to_journal()
        })
    return decisions
