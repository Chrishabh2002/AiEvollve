
import requests
import json
import time

try:
    r = requests.get("http://localhost:8000/api/world/feed?limit=5")
    posts = r.json()

    print(f"--- FEED ({len(posts)} items) ---")
    for p in posts:
        print(f"[{p['agent_id']}]")
        print(f"{p['content']}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
