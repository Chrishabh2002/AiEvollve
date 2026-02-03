import requests
import time
import json

# Wait for agents to process
time.sleep(10)

# Fetch feed
r = requests.get('http://localhost:8000/api/world/feed?limit=5')
posts = r.json()

print(f'\n=== FEED ({len(posts)} posts) ===\n')
for p in posts[:5]:
    print(f"[{p['agent_name']}]: {p['content'][:100]}")
    print(f"  Likes: {len(p['likes'])}, ID: {p['id'][:8]}...")
    print()
