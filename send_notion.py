#!/usr/bin/env python3
"""
Send Notion
=========
Sends data to Notion.
Usage: python3 send_notion.py
"""
import os, json, requests
from datetime import datetime, timezone
from pathlib import Path

NOTION_KEY = os.getenv("NOTION_API_KEY")


def send(data: dict):
    if not NOTION_KEY:
        print("No NOTION_KEY")
        return False
    print(f"Sent: {data}")
    return True

def main():
    send({"timestamp": datetime.now(timezone.utc).isoformat()})

if __name__ == "__main__":
    main()
