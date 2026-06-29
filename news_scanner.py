#!/usr/bin/env python3
"""
News Scanner
===========
Scans news feeds for kill factor detection.
Usage: python3 news_scanner.py
"""
import feedparser, re, json, os
from datetime import datetime, timezone, timedelta

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
NEWS_CACHE = os.path.join(WORKSPACE, "journal", "news_cache.json")

FEEDS = {
    "forexlive": {"url": "https://forexlive.com/feed", "weight": 1.0},
    "econotimes": {"url": "https://www.econotimes.com/rss", "weight": 0.6},
}

PAIR_KEYWORDS = {
    "EURUSD": ["EUR", "Euro", "ECB", "Federal Reserve", "Dollar", "USD", "US economy", "Eurozone"],
    "GBPUSD": ["GBP", "Pound", "Sterling", "BOE", "Bank of England", "Cable", "UK", "Britain"],
    "USDJPY": ["JPY", "Yen", "BOJ", "Bank of Japan", "Japan", "Tokyo", "Nikkei"],
    "AUDUSD": ["AUD", "Aussie", "RBA", "Reserve Bank of Australia", "Australia", "Commodities"],
    "XAUUSD": ["Gold", "XAU", "Precious metals", "Fed", "Inflation", "Safe haven", "DXY"],
}

CALENDAR_KEYWORDS = [
    "NFP", "non-farm payrolls", "CPI", "inflation", "GDP", "interest rate",
    "rate decision", "FOMC", "ECB meeting", "BOE rate", "RBA", "BOJ",
]

def load_cache():
    if os.path.exists(NEWS_CACHE):
        with open(NEWS_CACHE) as f:
            return json.load(f)
    return {"news": [], "kill": False}

def save_cache(cache):
    with open(NEWS_CACHE, "w") as f:
        json.dump(cache, f, indent=2)

def fetch_news():
    articles = []
    for name, feed in FEEDS.items():
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:10]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "source": name,
                    "published": entry.get("published", ""),
                })
        except Exception as e:
            print(f"Feed error {name}: {e}")
    return articles

def check_kill(articles):
    for article in articles:
        title = article.get("title", "").lower()
        for kw in CALENDAR_KEYWORDS:
            if kw.lower() in title:
                return True
    return False

def main():
    articles = fetch_news()
    cache = {
        "news": articles,
        "kill": check_kill(articles),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    save_cache(cache)
    print(f"News: {len(articles)} articles, kill={cache['kill']}")

if __name__ == "__main__":
    main()
