#!/usr/bin/env python3
"""Forex News system."""
import feedparser, re, json, os
from datetime import datetime, timedelta, timezone

WORKSPACE = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(WORKSPACE, "news")
os.makedirs(NEWS_DIR, exist_ok=True)

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

CALENDAR_KEYWORDS = ["NFP", "non-farm payrolls", "CPI", "inflation", "GDP", "interest rate", "rate decision", "FOMC", "ECB meeting", "BOE rate", "RBA", "BOJ"]


def fetch_news():
    articles = []
    for name, feed in FEEDS.items():
        try:
            parsed = feedparser.parse(feed["url"])
            for entry in parsed.entries[:10]:
                articles.append({"title": entry.title, "link": entry.link, "source": name, "published": entry.get("published", "")})
        except Exception as e:
            print(f"Feed error {name}: {e}")
    return articles

def filter_news(articles):
    filtered = []
    for article in articles:
        title = article.get("title", "").lower()
        for pair, keywords in PAIR_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in title:
                    article["pair"] = pair
                    filtered.append(article)
                    break
    return filtered

def main():
    articles = fetch_news()
    filtered = filter_news(articles)
    print(f"News: {len(filtered)} articles")

if __name__ == "__main__":
    main()
