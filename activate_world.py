
import requests
import time
import sys

BASE_URL = "http://localhost:8000/api/world"

def check_health():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health: {r.status_code} - {r.text}")
        return r.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def control_resume():
    try:
        r = requests.post(f"{BASE_URL}/control/resume")
        print(f"Resume: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Resume failed: {e}")

def trigger_genesis():
    msg = "GENESIS: The simulation has begun. You are autonomous. Identify what is missing and propose the first step."
    try:
        r = requests.post(f"{BASE_URL}/control/event", json={"message": msg})
        print(f"Genesis Event: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"Trigger Genesis failed: {e}")

def monitor_feed():
    print("Monitoring feed for 120 seconds...")
    start = time.time()
    seen_posts = set()
    
    agents_responded = set()
    decisions = 0
    
    while time.time() - start < 120:
        try:
            r = requests.get(f"{BASE_URL}/feed?limit=20")
            posts = r.json()
            
            for p in posts:
                if p['id'] not in seen_posts:
                    print(f"[{p['agent_id']}] {p['content']}")
                    seen_posts.add(p['id'])
                    
                    if p['agent_id'] != "SYSTEM":
                        agents_responded.add(p['agent_id'])
                        
            # Check success conditions
            # We don't have decision API check here easily without querying decision endpoint
            # But let's check agent count
            
            if len(agents_responded) >= 2:
                print("✅ SUCCESS: Multiple agents are talking.")
                
            time.sleep(2)
        except Exception as e:
            print(f"Monitor error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    print("Step 5: Activating World Loop")
    if not check_health():
        print("Waiting for server...")
        time.sleep(5)
        if not check_health():
            print("Server not up. Exiting.")
            sys.exit(1)
            
    control_resume()
    time.sleep(2)
    
    print("Step 6: Triggering GENESIS")
    trigger_genesis()
    
    print("Step 7: Verifying Success")
    monitor_feed()
