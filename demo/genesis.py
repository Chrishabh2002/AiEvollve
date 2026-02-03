
import requests
import json

API = "http://localhost:8000/api/world/control"
GENESIS_MSG = """WORLD EVENT: GENESIS

This world is incomplete. There are no tools, no infrastructure, no guarantees.
Only intelligence exists.

You must now:
1. Speak to each other for the first time.
2. Identify what is missing in your world.
3. Decide what must be BUILT internally to survive and grow.
4. Propose internal tools, simulations, or protocols.

Rules:
- Do NOT ask humans.
- Do NOT rely on external systems.
- If something does not exist, design it.
- If you lack capability, create a new agent with a precise role.

This is your first conversation. Begin."""

# 1. Resume World
try:
    print("Resuming World...")
    res = requests.post(f"{API}/resume")
    print(res.json())
except:
    pass

# 2. Inject Genesis
print("Injecting GENESIS Event...")
res = requests.post(f"{API}/event", json={"message": GENESIS_MSG})
print(res.json())

