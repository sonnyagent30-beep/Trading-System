#!/usr/bin/env python3
"""
Post to Notion
==========
Posts results to Notion.
Usage: python3 post_notion.py
"""
import os, json, requests
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path("/root/workspace/forex")
NOTION_KEY = os.getenv("NOTION_API_KEY")
NOTION_DB = os.getenv("NOTION_DB_ID")

def post_to_notion(data: dict):
    if not NOTION_KEY or not NOTION_DB:
        return False
    url = f"https://api.notion.com/v1/pages"
    headers = {"Authorization": f"Bearer {NOTION_KEY}", "Content-Type": "application/json"}
    payload = {
        "parent": {"database_id": NOTION_DB},
        "properties": {
            "Date": {"date": {"start": datetime.now(timezone.utc).isoformat()}},
            "Data": {"rich_text": [{"text": {"content": json.dumps(data)}}],
        },
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.status_code == 200

def main():
    data = {"test": "data"}
    post_to_notion(data)
    print("Posted to Notion")

if __name__ == "__main__":
    main()
