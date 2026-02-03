import requests

try:
    r = requests.get('http://localhost:8000/api/world/feed')
    posts = r.json()
    print(f'Total posts: {len(posts)}\n')

    # Show last 5 posts
    for p in posts[-5:]:
        agent_id = p.get('agent_name', p['agent_id'][:8])
        content = p['content']
        print(f'[{agent_id}]: {content}\n')
except Exception as e:
    print(e)
