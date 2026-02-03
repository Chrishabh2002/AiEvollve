import requests
import time

time.sleep(8)
r = requests.get('http://localhost:8000/api/world/feed')
posts = r.json()
print(f'Total posts: {len(posts)}')
for p in posts[:10]:
    print(f"\n[{p['agent_id']}]: {p['content'][:200]}")
