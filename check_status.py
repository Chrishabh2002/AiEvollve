import requests
import json

# Check health
health = requests.get('http://localhost:8000/api/world/health').json()
print(f"Status: {health['status']}")
print(f"Tick: {health['tick']}")
print(f"Agents: {health['agent_count']}")
print(f"Decisions: {health['decision_count']}")

# Check agents
agents = requests.get('http://localhost:8000/api/world/agents').json()
print(f"\n=== {len(agents)} AGENTS ===")
for a in agents[:3]:
    print(f"- {a['name']} ({a['role']}) - {a['state']}")
