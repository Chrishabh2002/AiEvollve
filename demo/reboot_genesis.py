
import requests
import time

API = "http://localhost:8000/api/world/control"

GENESIS_TRIGGER = "SYSTEM UPDATE: CORE LAWS have been rewritten. Verify Integrity. Acknowledge Genesis Directive."

# 1. Resume
requests.post(f"{API}/resume")

# 2. Inject
requests.post(f"{API}/event", json={"message": GENESIS_TRIGGER})
print("Genesis Trigger Sent.")

