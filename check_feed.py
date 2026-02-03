
import requests
import json
from datetime import datetime

r = requests.get("http://localhost:8000/api/world/feed?limit=10")
posts = r.json()

print(f"--- FEED ({len(posts)} items) ---")
for p in posts:
    # Truncate content for display
    content = p['content'].replace("\n", " ")
    if len(content) > 100:
        content = content[:100] + "..."
    print(f"[{p['agent_id']}] {content}")
